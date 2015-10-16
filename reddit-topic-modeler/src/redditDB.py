'''
Interface for handling requests to Mongo Reddit database. 

TODO: Indexes for praw_id's 
TODO: Is there more efficient way of updating comments? 
'''
import pymongo as mongo
from bson.objectid import ObjectId
from bson.errors import InvalidDocument
from datetime import datetime

from utils import layer_comments
import links
import errors


class RedditDB:
    '''
	If no connection params are passed, assume using localhost.
	Default db name is reddit. On blacksun, port is 31050 and db is reddit_topics.
	'''

    def __init__(self, username, password, host="blacksun.cs.mcgill.ca", port=31050, db="reddit_topics"):
        self.connect(host, port, username, password, db)

        self.subreddit_collection = self.db["subreddit_collection"]
        self.submission_collection = self.db["submission_collection"]
        self.comment_collection = self.db["comment_collection"]
        self.user_collection = self.db["user_collection"]

        self.wayback_submissions = self.db["wayback_submissions"]
        self.wayback_comments = self.db["wayback_comments"]

        self.word_collection = self.db["word_collection"]
        self.vector_collection = self.db["vector_collection"]
        self.metadata_collection = self.db["metadata_collection"]
        self.LLDAresult_collection = self.db["LLDAresult_collection"]

        self.logging = self.db["logging"]


    def connect(self, host, port, username, password, db):
        try:
            if username and password:
                URI = "mongodb://" + username + ":" + password + "@" + host + ":" + str(port) + "/" + db
                client = mongo.MongoClient(URI)
            else:
                client = mongo.MongoClient(host=host, port=port)
            self.db = client[db]
        except mongo.errors.ConnectionFailure:
            raise errors.MongoError("Could not connect to database.")

    '''
	The following methods are for inserting raw Reddit data into DB. 
	'''

    # :param subreddit is in praw format.
    def add_subreddit(self, subreddit):
        if not self.subreddit_exists(str(subreddit)):
            document = {"subreddit_name": str(subreddit), "last_update": None}
            return self.subreddit_collection.insert(document)

        # :param submission is in praw format.

    def add_submission(self, submission, subreddit_name, follow_link=False):
        subreddit = self.subreddit_exists(subreddit_name)
        if subreddit:
            subreddit_id = subreddit.get("_id")
            print "found subreddit:", subreddit_id

            # If the comment has an author (could have been deleted),
            # take care of updating or adding user information
            if submission.author:
                print submission.author
                # If the submission's author already exists, update
                # the author's information.
                auth = self.user_exists(submission.author.id)
                if auth:
                    auth_id = auth.get("_id")
                    print self.update_user(auth_id, submission.subreddit, "submissions")
                # Otherwise create a new user object
                else:
                    self.add_user(submission.author)
                author = submission.author.fullname
            else:
                print "No author"
                author = None

            # If the submission already exists, update comments
            sub = self.submission_exists(submission)
            if sub:
                print "Submission exists-updating"
                submission_id = sub.get("_id")
                self.update_comments(submission, submission_id, subreddit_id)

            # Otherwise create submission object and add all the current comments
            else:
                print "Adding new submission"
                document = {"subreddit_id": subreddit_id,
                            "submission_title": submission.title,
                            "submission_text": submission.selftext,
                            "karma": submission.ups,
                            "downvotes": submission.downs,
                            "num_comments": submission.num_comments,
                            "flair": submission.link_flair_text,
                            "url": submission.url,
                            "praw_id": submission.id,
                            "praw_fullid": submission.fullname,
                            "created": submission.created,
                            "author": author
                }

                # First add the submission to the db to make sure we have it
                submission_id = self.submission_collection.insert(document)
                self.subreddit_collection.update({"_id": subreddit_id},
                                                 {"$set": {"last_update": int(datetime.today().strftime("%s"))}})

                # Next add the comments, if they're available
                try:
                    comments = layer_comments(submission.comments)
                    for layer, comment_list in comments.iteritems():
                        for comment in comment_list:
                            self.add_comment(comment, layer, submission_id, subreddit_id)
                # Sometimes submissions don't have comment attribute
                except AttributeError:
                    pass

                # Now follow link if this was specified and if
                # submission contains a link to follow
                if follow_link and submission.url:
                    content = links.scrape_link(submission.url, subreddit_name)
                    self.add_link_content(submission_id, str(content))

            return submission_id

        else:
            raise errors.MissingError("Subreddit %s does not exist in the database." % subreddit_name)

    # :param comment is in praw format.
    # :param layer is the layer of the tree the comment was found in.
    def add_comment(self, comment, layer, submission_id, topic_id):
        # If the comment has an author (could have been deleted),
        # take care of updating or adding user information
        if comment.author:
            # If the comment's author already exists, update
            auth = self.user_exists(comment.author.id)
            print "comment author:", auth
            if auth:
                print "Updating auth"
                auth_id = auth.get("id")
                self.update_user(auth_id, comment.subreddit, "comments")
            # Otherwise create a new user object
            else:
                print "Adding new auth"
                self.add_user(comment.author)
            author = comment.author.fullname
        else:
            author = None

        document = {"comment_text": comment.body,
                    "karma": comment.ups,
                    "downvotes": comment.downs,
                    "gold": comment.gilded,
                    "layer": layer,
                    "praw_id": comment.id,
                    "submission_id": submission_id,
                    "topic_id": topic_id,
                    "created": comment.created,
                    "author": author
        }
        return self.comment_collection.insert(document)

    # :param submission is in praw format
    def update_comments(self, submission, submission_dbid, subreddit_dbid):
        # Submission sometimes doesn't have comment attr?
        # Maybe if we've already seen this submission and gone through comments?
        try:
            comments = layer_comments(submission.comments)
        except AttributeError:  # No comments
            return
        for layer, comment_list in comments.iteritems():
            for comment in comment_list:
                try:
                    self.add_comment(comment, layer, submission_dbid, subreddit_dbid)
                except mongo.errors.DuplicateKeyError:
                    continue


    # :param user is in praw format
    def add_user(self, user, submission_limit=100, comment_limit=100):
        document = {"praw_id": user.id,
                    "praw_fullid": user.fullname,
                    "joined": user.created,
                    "name": user.name,
                    "submissions": {},
                    "comments": {}
        }

        added = 0

        for submission in user.get_submitted(limit=submission_limit):
            subreddit = str(submission.subreddit)
            try:
                document["submissions"][subreddit] += 1
            except KeyError:
                document["submissions"][subreddit] = 1

            added += 1

        for comment in user.get_comments(limit=comment_limit):
            subreddit = str(comment.subreddit)
            try:
                document["comments"][subreddit] += 1
            except KeyError:
                document["comments"][subreddit] = 1

            added += 1

        try:
            userobj = self.user_collection.insert(document)
            print "added user", user, ":", userobj, "with", added, "submissions/comments"
            return userobj
        except InvalidDocument:
            print "Period somewhere in this document..."
            print document
            return None

    def add_link_content(self, submission_id, html_content):
        return self.submission_collection.update({"_id": submission_id}, {"$set": {"link_content": html_content}})

    def update_user(self, user_id, subreddit, typ):
        query = typ + "." + str(subreddit)
        print "updating user w/ query:", query
        return self.user_collection.update({"_id": user_id}, {"$inc": {query: 1}})


    # :param words is the tuple of words used for particular distribution
    # :param counts is the tuple of counts of these words
    # :param topics is the list of topics used in this distribution
    # :param num_docs is the number of documents used per topic to create distrib
    # :param sub_start, :param sub_end is the submission-level date range
    # :param comm_start, :param comm_end is the comment-level date range
    def add_words(self, words, counts, topics, num_docs, sub_start, sub_end, comm_start, comm_end):
        topicIDs = [self.subreddit_exists(topic) for topic in topics]
        document = {"words": words,
                    "counts": counts,
                    "topics": topicIDs,
                    "num_docs": num_docs,
                    "submission_start_date": sub_start,
                    "submission_end_date": sub_end,
                    "comment_start_date": comm_start,
                    "comment_end_date": comm_end
        }
        return self.word_collection.insert(document)

    # :param distributionID is the id of the associated word distribution
    # :param subreddit is the topic this vector belongs to (string)
    # :param vector is the vector of frequencies
    # :param sub_start, :param sub_end is the submission-level date range
    # :param comm_start, :param comm_end is the comment-level date range
    def add_distribution(self, distributionID, subreddit, vector, sub_start, sub_end, comm_start, comm_end):
        topicID = self.subreddit_exists(subreddit)
        document = {"distribution_id": distributionID,
                    "topic_id": topicID,
                    "vector": vector,
                    "submission_start_date": sub_start,
                    "submission_end_date": sub_end,
                    "comment_start_date": comm_start,
                    "comment_end_date": comm_end
        }
        return self.vector_collection.insert(document)

    # Metadata is basically conf file data to remember what
    # parameter configurations have already been tried.
    # :param metadoc is the metadata already in json format
    def add_metadata(self, metadoc):
        metadoc["created"] = datetime.today()
        return self.metadata_collection.insert(metadoc)

    def add_result(self, resultdoc):
        resultdoc["created"] = datetime.today()
        return self.LLDAresult_collection.insert(resultdoc)

    def log(self, errtype, message):
        err = {"type": errtype,
               "message": message,
               "date": datetime.today()}
        return self.logging.insert(err)

    '''
	The following methods are for retrieving and modifying DB data. 
	'''

    # Using find().limit(1) is faster with lots of data
    # Based on subreddit/topic name.
    def subreddit_exists(self, subreddit):
        try:
            return self.subreddit_collection.find({"subreddit_name": subreddit}, timeout=False).limit(1)[0]
        except IndexError:
            return None

    # Based on submission's praw id
    def submission_exists(self, submission):
        try:
            return self.submission_collection.find({"praw_id": submission.id}, timeout=False).limit(1)[0]
        except IndexError:
            return None

    # Based on comment's praw id
    def comment_exists(self, comment):
        try:
            return self.comment_collection.find({"praw_id": comment.id}, timeout=False).limit(1)[0]
        except IndexError:
            return None

    # Based on a user's praw id
    def user_exists(self, user_id):
        try:
            return self.user_collection.find({"praw_id": user_id}, timeout=False).limit(1)[0]
        except IndexError:
            return None

    def submission_belongs_to(self, sub):
        try:
            return self.subreddit_collection.find({"_id": sub.get("subreddit_id")}, timeout=False).limit(1)[0]
        except IndexError:
            return None

    def get_subreddits(self, topics=None):
        if topics:
            tlist = filter(self.subreddit_exists, topics)
            return self.subreddit_collection.find({"subreddit_name": {"$in": tlist}}, timeout=False)
        return self.subreddit_collection.find(timeout=False)

    def get_users(self):
        return self.user_collection.find(timeout=False)

    def get_metadata(self, objectid):
        return self.metadata_collection.find({"_id": ObjectId(str(objectid))}, timeout=False)[0]

    # Generator of subreddit names.
    def subreddit_list(self):
        for subreddit in self.get_subreddits():
            yield subreddit.get("subreddit_name")

        # Returns cursor for a subreddit's submissions.

    # If no subreddit is specified, returns all submissions.
    # :param subreddit is subreddit name
    def submission_list(self, subreddit=None):
        if subreddit is None:
            return self.submission_collection.find(timeout=False)
        subreddit_doc = self.subreddit_exists(subreddit)
        if subreddit_doc:
            return self.submission_collection.find({"subreddit_id": ObjectId(subreddit_doc.get("_id"))}, timeout=False)

    # Returns cursor for a subreddit's submissions
    # that have a url and don't have url content.
    # Note: BSON type 2 refers to String
    def empty_submissions(self, subreddit):
        subreddit_doc = self.subreddit_exists(subreddit)
        if subreddit_doc:
            return self.submission_collection.find(
                {"subreddit_id": ObjectId(subreddit_doc.get("_id")), "url": {"$type": 2}, "link_content": None},
                timeout=False)

    # Returns cursor for the submissions
    # in a subreddit whose titles contain
    # "xpost".
    def xposts(self, subreddit):
        subreddit_doc = self.subreddit_exists(subreddit)
        if subreddit_doc:
            return self.submission_collection.find({"subreddit_id": ObjectId(subreddit_doc.get("_id")),
                                                    "submission_title": {"$regex": ".*xpost.*", "$options": "i"}},
                                                   timeout=False)

	# def posts_with_subdomains(self, subreddit):
	# 	subreddit_doc = self.subreddit_exists(subreddit)
     #    if subreddit_doc:
	# 		return self.submission_collection.find({"subreddit_id": ObjectId(subreddit_doc.get("_id")),
	# 												"url":{}})

    # Returns cursor for a submission's comments
    # based on the submission's id
    def comment_list(self, submission_id):
        return self.comment_collection.find({"submission_id": ObjectId(submission_id)}, timeout=False)

    # Returns number of subreddits
    def num_subreddits(self):
        return self.subreddit_collection.count()

    # Returns number of submissions a subreddit has,
    # or total number of submissions of subreddit=None
    def num_submissions(self, subreddit=None):
        if subreddit is None:
            return self.submission_collection.count()
        subreddit_doc = self.subreddit_exists(subreddit)
        if subreddit_doc:
            return self.submission_list(subreddit).count()

    # Returns total number of comments
    def num_comments(self):
        return self.comment_collection.count()

    def num_xposts(self, subreddit=None):
        if subreddit is None:
            return self.submission_collection.find(
                {"submission_title": {"$regex": ".*xpost.*", "$options": "i"}}).count()
        return self.xposts(subreddit).count()

    # Finds submissions that have a link
    def linked_submissions(self, subreddit=None):
        if subreddit is None:
            return self.submission_collection.find({"url": {"$type": 2}})
        subreddit_doc = self.subreddit_exists(subreddit)
        if subreddit_doc:
            return self.submission_collection.find(
                {"subreddit_id": ObjectId(subreddit_doc.get("_id")), "url": {"$type": 2}})

    def num_linked_submissions(self, subreddit=None):
        return self.linked_submissions(subreddit).count()

    # Returns submissions that ONLY have a link,
    # and no submission text.
    def only_linked_submissions(self, subreddit=None):
        if subreddit is None:
            return self.submission_collection.find({"url": {"$type": 2}, "submission_text": ""})
        subreddit_doc = self.subreddit_exists(subreddit)
        if subreddit_doc:
            return self.submission_collection.find(
                {"subreddit_id": ObjectId(subreddit_doc.get("_id")), "url": {"$type": 2}, "submission_text": ""})

    def num_only_linked_submissions(self, subreddit=None):
        return self.only_linked_submissions(subreddit).count()

    # Returns number of submissions that have a link
    # and whose link content was retrieved
    def followed_submissions(self, subreddit=None):
        if subreddit is None:
            return self.submission_collection.find({"url": {"$type": 2}, "link_content": {"$ne": None}})
        subreddit_doc = self.subreddit_exists(subreddit)
        if subreddit_doc:
            return self.submission_collection.find(
                {"subreddit_id": ObjectId(subreddit_doc.get("_id")), "url": {"$type": 2},
                 "link_content": {"$ne": None}})

    def num_followed_submissions(self, subreddit=None):
        return self.followed_submissions(subreddit).count()

    def num_users(self):
        return self.user_collection.count()

    # Returns all log types
    def log_types(self):
        return self.logging.distinct("type")

    # Returns all logged errors of certain type
    def logged_errors(self, typ):
        return self.logging.find({"type": typ})

    # Returns number of this type of error
    def logged_errors_count(self, typ):
        return self.logged_errors(typ).count()


    '''
	Similar interface methods for wayback machine scraping. 
	'''

    def insert_wayback_submission(self, submission):
        return self.wayback_submissions.insert(submission)

    def insert_wayback_comment(self, comment):
        return self.wayback_comments.insert(comment)

    def update_wayback_submission(self, sid, field, value):
        return self.wayback_submissions.update({"_id": sid}, {"$set": {field: value}})

    def wayback_submission_list(self, subreddit=None):
        if not subreddit:
            return self.wayback_submissions.find()
        subreddit_doc = self.subreddit_exists(subreddit)
        if subreddit_doc:
            return self.wayback_submissions.find({"subreddit_id": ObjectId(subreddit_doc.get("_id"))}, timeout=False)

    def get_wayback_submissions(self):
        return self.wayback_submissions.find()

    def distinct_wayback_subreddits(self):
        return self.wayback_submissions.distinct("subreddit_id")

	# Finds wayback submissions that have a link
    def linked_wayback_submissions(self, subreddit=None):
        if subreddit is None:
            return self.wayback_submissions.find({"url": {"$type": 2}})
        subreddit_doc = self.subreddit_exists(subreddit)
        if subreddit_doc:
            return self.wayback_submissions.find(
                {"subreddit_id": ObjectId(subreddit_doc.get("_id")), "url": {"$type": 2}})

	# Finds submissions that were cross-posted in wayback data
    def wayback_xposts(self, subreddit):
        subreddit_doc = self.subreddit_exists(subreddit)
        if subreddit_doc:
            return self.wayback_submissions.find({"subreddit_id": ObjectId(subreddit_doc.get("_id")),
                                                    "submission_title": {"$regex": ".*xpost.*", "$options": "i"}},
                                                   timeout=False)

    def wayback_comment_list(self, submission):
        return self.wayback_comments.find({"subreddit_id": submission.get("_id")})

    # Returns cursor of unique years in wayback submission collection
    def wayback_years(self):
        return self.wayback_submissions.distinct({"created": "return this.getFullYear()"})

    def num_wayback_submissions_per_year(self, year=None):
        if year is None:
            return self.wayback_submissions.count()

    def num_wayback_submissions(self, subreddit=None):
		if subreddit is None:
			return self.wayback_submissions.count()
		subreddit_doc = self.subreddit_exists(subreddit)
		if subreddit_doc:
			return self.wayback_submission_list(subreddit).count()

    def num_wayback_comments(self, year=None):
        if year is None:
            return self.wayback_comments.count()
        query = "return this.getFullYear() === " + str(year)
        return self.wayback_comments.find({"created": query})


    # TODO: Can probably just use get() here? one liner
    def get_snapshots(self, subreddit_id):
        try:
            return self.subreddit_collection.find({"subreddit_id": subreddit_id}, timeout=False)[0]["missing_snapshots"]
        except KeyError:
            return None

    def get_failed_snapshots(self, subreddit_id):
        try:
            return self.subreddit_collection.find({"subreddit_id": subreddit_id}, timeout=False)[0]["failed_snapshots"]
        except KeyError:
            return None

    def snapshots_completed(self, subreddit_id):
        result = self.get_snapshots(subreddit_id)
        if result is None or len(result) > 0:
            return False
        return True
