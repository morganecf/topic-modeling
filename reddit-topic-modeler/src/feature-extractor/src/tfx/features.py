import collections
import json
import logging
import operator
import os

from tfx import errors, resultparse, utils


"""
The base feature class that all others inherit from
"""

class FeatureBase:
    needs_users = False

    def save_params(self):
        pass

    def initialise(self, labels):
        pass

    def __init__(self, params, default_params):
        self.name = self.__class__.__name__
        self.params = params
        self.default_params = default_params

        # Save and validate any parameters that could apply to all features
        features_file = self.get_param('features_file', required=False)
        if features_file is not None and utils.is_str(features_file):
            logging.debug("Opening the feature file %s for %s" %
                          (features_file, self))

            # If the features file exists, open it, read the features
            result_parser = resultparse.ResultParser()
            result_parser.load(features_file)
            self.feature_data = result_parser.get_feature_data(self.name)
            self.needs_users = False
        else:
            self.feature_data = None

        # Save feature-specific parameters
        self.save_params()

    def get_param(self, param, required=True):
        """
        Look for the specified parameter first in the feature-specific
        configuration; if it doesn't exist there, use the default parameters.

        If this parameter is required and it doesn't exist in either, raise an
        error; if it's not required but can't be found, return None.
        """
        if param in self.params:
            return self.params[param]
        else:
            if param in self.default_params:
                return self.default_params[param]
            elif required:
                raise errors.ConfFileError("Required parameter %s not found" \
                                           % param)

    def __str__(self):
        return self.__class__.__name__

    def get_data(self, user):
        return user.data[self.entity]

    def get_needed_entities(self):
        """
        Returns a list of the entities needed (as strings).
        Should be overridden for all features that need more than one entity.
        """
        return [self.entity]

    def extract_feature(self, user):
        pass

    def get_info(self):
        """
        Called when saving to the results file. Usually {} is fine.
        """
        return {}


"""
The Naive Bayes features
"""

class NaiveFeatureBase(FeatureBase):
    def initialise(self, labels):
        # Do this later
        pass

    def extract_feature(self, user):
        user_data = self.get_data(user)

        return []


class NaiveWords(NaiveFeatureBase):
    entity = 'words'


class NaiveDigrams(NaiveFeatureBase):
    entity = 'digrams'


class NaiveTrigrams(NaiveFeatureBase):
    entity = 'trigrams'


class NaiveStems(NaiveFeatureBase):
    entity = 'stems'


class NaiveCostems(NaiveFeatureBase):
    entity = 'costems'


class NaiveHashtags(NaiveFeatureBase):
    entity = 'hashtags'



"""
k-top features
"""

class KTopFeatureBase(FeatureBase):
    needs_users = True
    info = {}

    # Make sure that k is defined, and of the right type
    def save_params(self):
        k = self.get_param('k')

        if type(k) is not int or k < 1:
            raise errors.ConfFileError("k needs to be a positive int")

        self.k = k

    def initialise(self, labels):
        # If we've initialised from the features file, ignore users
        if self.feature_data:
            logging.debug("Using features file for %s" % self)
            self.info = self.feature_data
            labels = self.info['order']

            # Limit it to the first k
            self.k_top = self.info[labels[0]][:self.k] + \
                         self.info[labels[1]][:self.k]
        else:
            logging.debug("About to figure out k-top for %s" % self)
            self.label_counters = {}

            for label in labels:
                self.label_counters[label] = collections.defaultdict(int)

            self.labels = labels

            logging.debug("Done with the defaultdict initialisation, about to fill")

    def init_with_user(self, label, user):
        user_entities = self.get_data(user)

        for entity, entity_count in user_entities.iteritems():
            self.label_counters[label][entity] += entity_count

    def finish_init(self):
        label_1 = self.labels.keys()[0]
        label_2 = self.labels.keys()[1]
        difference_1 = {}
        for thing in self.label_counters[label_1]:
            difference_1[thing] = (self.label_counters[label_1][thing] -
                self.label_counters[label_2][thing])

        difference_2 = {}
        for thing in self.label_counters[label_2]:
            difference_2[thing] = (self.label_counters[label_2][thing] -
                self.label_counters[label_1][thing])

        logging.debug("Done filling the defaultdicts, about to sort etc")

        top_differences_1 = sorted(difference_1.iteritems(),
            key=operator.itemgetter(1),
            reverse=True)
        top_differences_2 = sorted(difference_2.iteritems(),
            key=operator.itemgetter(1),
            reverse=True)

        logging.debug("Done sorting")

        get_entity = operator.itemgetter(0)
        k_top_1 = map(get_entity, top_differences_1[:self.k])
        k_top_2 = map(get_entity, top_differences_2[:self.k])
        self.k_top = k_top_1 + k_top_2

        self.info = {
            label_1: k_top_1,
            label_2: k_top_2,
            "order": [label_1, label_2],
        }

        logging.debug("Figured out k-top for %s" % self)

    def extract_feature(self, user):
        # Returns a list
        return map(self.get_data(user).__getitem__, self.k_top)

    def get_info(self):
        return self.info

class KTopWords(KTopFeatureBase):
    entity = 'words'


class KTopDigrams(KTopFeatureBase):
    entity = 'digrams'


class KTopTrigrams(KTopFeatureBase):
    entity = 'trigrams'


class KTopStems(KTopFeatureBase):
    entity = 'stems'


class KTopCostems(KTopFeatureBase):
    entity = 'costems'


class KTopHashtags(KTopFeatureBase):
    entity = 'hashtags'



"""
Frequency features
"""


class FrequencyFeatureBase(FeatureBase):
    def get_needed_entities(self):
        return [self.entity, 'tweeting_time']

    def extract_feature(self, user):
        """
        Returns the number of [entity] per day.
        """
        tweeting_time = user.data['tweeting_time'] / 86400
        if tweeting_time == 0:
            return [0.0]
        else:
            return [self.get_data(user) / tweeting_time]


class TweetFrequency(FrequencyFeatureBase):
    entity = 'num_tweets'


# retweets are considered mentions
class MentionFrequency(FrequencyFeatureBase):
    entity = 'num_mentions'


class HashtagFrequency(FrequencyFeatureBase):
    entity = 'num_hashtags'


class LinkFrequency(FrequencyFeatureBase):
    entity = 'num_urls'


class RetweetFrequency(FrequencyFeatureBase):
    entity = 'num_retweets'



"""
The ratio features.
"""

class RatioFeatureBase(FeatureBase):
    def extract_feature(self, user):
        numerator = user.data[self.numerator]
        denominator = user.data[self.denominator]

        if denominator == 0:
            return [0]
        else:
            return [numerator * 1.0 / denominator]

    def get_needed_entities(self):
        return [self.numerator, self.denominator]


class InOutRatio(RatioFeatureBase):
    numerator = 'num_followers'
    denominator = 'num_friends'


class RetweetTweetRatio(RatioFeatureBase):
    numerator = 'num_retweets'
    denominator = 'num_tweets'



class NameFeature(FeatureBase):
    entity = 'name'

    def __init__(self, params, default_params):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        names_file_path = os.path.join(current_dir, 'resources', 'names.json')
        self.names = json.load(open(names_file_path))

        # If the threshold argument is passed, save it
        threshold = params.get('threshold') or default_params.get('threshold')
        self.threshold = None

        if threshold:
            if type(threshold) == float:
                self.threshold = threshold
                logging.debug("Threshold is %.2f" % threshold)
            else:
                raise errors.ConfFileError("Threshold (for the name feature)" +
                    " must be a float!")

    def extract_feature(self, user):
        user_name = self.get_data(user)

        # Make it upper-case and take everything before the first space
        if user_name is not '':
            first_name = user_name.upper().split()[0]
            value = self.names.get(first_name, 0.0)
        else:
            value = 0.0

        # If value is greater than a certain threshold, don't generate vector
        # Instead, let the list of users be thrown out (or saved)
        if self.threshold is not None:
            logging.debug("User, value of %.3f" % value)

            if abs(value) >= self.threshold:
                label = 'female' if value < 0 else 'male'
                logging.debug("Don't need this user")
                raise errors.UserNotNeeded(user.user_id, label)

        return [value]
