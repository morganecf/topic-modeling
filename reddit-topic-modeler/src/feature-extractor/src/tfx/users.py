import logging

from tfx import database, entities, errors, utils


tweet_extractors = []
profile_extractors = []
other_extractors = []


class User:
    def __init__(self, user_id, profile, tweets, uni):
        self.user_id = user_id
        self.profile = profile
        self.username = profile['screen_name']
        self.tweets = tweets
        self.data = {}

        self.unicode = uni 

        self.get_tweet_entities(tweet_extractors)
        self.get_profile_entities(profile_extractors)
        self.get_other_entities(other_extractors)

        logging.debug("Creating user %s (ID: %s)" % (self.username, user_id))

    def get_tweet_entities(self, extractors):
        # Prepare each extractor for this new user
        for extractor in extractors:
            extractor.initialise_for_user()

        # Go through all the tweets, extract
        for message, timestamp in self.tweets:
            cleaned_message = utils.clean(message, self.unicode)

            for extractor in extractors:
                extractor.get_tweet_entities(message, cleaned_message, timestamp)

        # Now save all the entity info
        for extractor in extractors:
            self.data[extractor.entity] = extractor.get_user_entities()

    def get_profile_entities(self, extractors):
        for extractor in extractors:
            self.data[extractor.entity] = extractor.get_user_entities(self.profile)

    def get_other_entities(self, extractors):
        for extractor in extractors:
            self.data[extractor.entity] = extractor.get_user_entities(self.data)

    def generate_feature_vector(self, enabled_features):
        feature_vector = []
        for feature in enabled_features:
            print feature, len(feature.extract_feature(self))
            feature_vector.extend(feature.extract_feature(self))

        return feature_vector

    def __repr__(self):
        return "%s" % self.user_id


class UserSet:
    def __init__(self, conf):
        self.unicode = True if conf.unicode == u"y" else False

        self.connection = database.Connection(self.unicode, **conf.mysql)
        self.labels = conf.labels
        self.user_ids = {}
        self.limits = {}

        for label, value in self.labels.iteritems():
            label_ids = []
            try:
                label_id = value["id"]
                if type(label_id) == int:
                    label_ids.append(label_id)
                elif type(label_id) == list:
                    label_ids.extend(label_id)
                else:
                    raise errors.ConfFileError("Label id should be an int or list.")
                self.limits[label] = value["limit"]
            except KeyError:
                raise errors.ConfFileError("Labels should have a label id and limit.")
            
            self.user_ids[label] = self.connection.get_users_for_label(label_ids)

        self.ignore_number = conf.ignore_number
        self.ignore_start = conf.ignore_start

    def get_users(self, label):
        """
        Uses a generator
        """
        # If one is set, both must be set (see confparse)
        if self.ignore_number is not None:
            self.ignore_end = self.ignore_start + self.ignore_number
        else:
            self.ignore_end = 0

        num_users = 0

        # Get the limit associated with this label 
        limit = self.limits[label]

        for i, user_id in enumerate(self.user_ids[label]):
            # If we need to ignore this user, skip
            if self.ignore_start <= i < self.ignore_end:
                continue

            user_profile = self.connection.get_profile_for_user(user_id)
            user_tweets = self.connection.get_tweets_for_user(user_id)

            # If there is no profile or tweet data for this user, skip
            if user_profile and user_tweets:
                user = User(user_id, user_profile, user_tweets, self.unicode)
                num_users += 1
                logging.debug("User number %d of label %s" % (num_users, label))

                yield user

                # Stop when we hit the limit (if the limit is not 0)
                if limit and num_users == limit:
                    break

        # If we haven't hit the limit by the time we're here, that's bad
        if limit and num_users < limit:
            error_message = ("There are only %d valid users for label %s "
                             "in the database. %d are required. Either "
                             "decrease the limit or add more users to the "
                             "database." % (num_users, label, limit))
            raise errors.MissingDataError(error_message)

    def process_entities(self, needed_entities):
        for entity in needed_entities:
            if entity in entities.tweet_extractors:
                tweet_extractors.append(entities.tweet_extractors[entity])
            elif entity in entities.profile_extractors:
                profile_extractors.append(entities.profile_extractors[entity])
            elif entity in entities.other_extractors:
                this_entity = entities.other_extractors[entity]
                other_extractors.append(this_entity)

                # Add all the entities this one depends on to the list
                # FIX THIS! temp. recursion?
                needed = this_entity.get_needed_entities()
                for needed_entity in needed:
                    if needed_entity in entities.tweet_extractors:
                        tweet_extractors.append(entities.tweet_extractors[needed_entity])
                    elif needed_entity in entities.profile_extractors:
                        profile_extractors.append(entities.profile_extractors[needed_entity])
            else:
                continue
