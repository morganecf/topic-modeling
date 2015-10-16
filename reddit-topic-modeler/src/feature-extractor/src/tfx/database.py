import cjson
import logging
import operator

import MySQLdb as mysql

from tfx import errors


class Connection:
    def __init__(self, uni, host, user, passwd, db):
        try:
            if uni:
                db = mysql.connect(host=host, user=user, passwd=passwd, db=db, charset='utf8')
            else:
                db = mysql.connect(host=host, user=user, passwd=passwd, db=db)
        except mysql.Error:
            raise errors.ConfFileError("Invalid MySQL connection details.")

        self.cursor = db.cursor()

    def get_users_for_label(self, labels):
        user_ids = []
        intersects = []
        unions = []
        for label in labels:
            if type(label) == int:
                unions.append(label)
            else:
                intersects.extend(label)

        # First get the users that have several labels (intersection)
        intersection = '('+','.join(map(lambda x: str(x), intersects))+')'
        count = len(intersects)
        if count > 0:
            SQLi = "SELECT user_id, count(*) as c FROM user_label_assignments WHERE label_id IN "+intersection+" GROUP BY user_id HAVING c = "+str(count)
            self.cursor.execute(SQLi)
            user_ids.extend([row[0] for row in self.cursor.fetchall()])

        # Now get all other users with specified labels (union of users)
        union = ' or '.join(map(lambda x: 'label_id = '+str(x), unions))
        SQLu = "SELECT user_id FROM user_label_assignments WHERE "+union
        self.cursor.execute(SQLu)
        user_ids.extend([row[0] for row in self.cursor.fetchall()])
        return user_ids

    def get_friends_for_user(self, user_id):
        self.cursor.execute("SELECT json_list FROM friends "
                            "WHERE user_id = %s "
                            "ORDER BY view_timestamp DESC "
                            "LIMIT 1", user_id)
        result = self.cursor.fetchall()
        
        try:
            json_list = result[0][0]
        except IndexError:
            log.warn("Missing entry in friends for %s" % user_id)
            return []

        try:
            friends_list = cjson.decode(json_list)
        except cjson.DecodeError:
            log.warn("Invalid json_list in friends for %s" % user_id)
            return []

    def get_profile_for_user(self, user_id):
        self.cursor.execute("SELECT json_source FROM user_profiles "
                            "WHERE user_id = %s "
                            "ORDER BY view_timestamp DESC "
                            "LIMIT 1", user_id)
        result = self.cursor.fetchall()

        try:
            json_source = cjson.decode(result[0][0])
            return json_source
        except IndexError:
            logging.debug("No row in user_profiles for %s" % user_id)
        except cjson.DecodeError:
            logging.debug("Invalid JSON in user_profiles for %s" % user_id)

        return {}

    def get_tweets_for_user(self, user_id):
        self.cursor.execute("SELECT status_text, tweet_timestamp FROM user_tweets "
                            "WHERE user_id = %s", user_id)
        result = self.cursor.fetchall()

        return result
