from google.appengine.ext import ndb
import logging


class UserDetails(ndb.Model):
    email = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    admin = ndb.BooleanProperty(default=False)

    @classmethod
    def first_user_exists(cls):
        query_results = cls.query().fetch()
        if query_results:
            return True
        else:
            return False

    @classmethod
    def is_user_admin(cls,email):
        logging.info(email)
        query_results = cls.query(ndb.AND(cls.email == email, cls.admin == True)).get()
        if query_results:
            return True
        else:
            return False

    @classmethod
    def is_user_authenticated(cls, email):
        query_results = cls.query(cls.email == email).get()
        if query_results:
            return True
        else:
            return False

    @classmethod
    def get_authenticated_user(cls, email):
        query_results = cls.query(cls.email == email).get()
        if query_results:
            return query_results
        else:
            return None

    @classmethod
    def get_users_for_type(cls, type,cursor,limit):
        if type.lower() == 'admin':
            query_results,cursor,more = cls.query(cls.admin == True).fetch_page(int(limit),start_cursor=cursor)
        else:
            query_results,cursor,more = cls.query(cls.admin == False).fetch_page(int(limit), start_cursor=cursor)
        return query_results, cursor, more