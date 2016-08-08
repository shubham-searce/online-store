import json
import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb
from app.user.utils_user import *
from app.user.models_user import *
import time

class UserHandler(webapp2.RequestHandler):
    def post(self):
        user_email = users.get_current_user().email()
        logging.info("Request raised by : %s",user_email)

        if UserDetails.is_user_admin(user_email):
            try:
                json_input = json.loads(self.request.body)
            except Exception,e:
                self.response_handler({"message": "No input received or invalid input", "error":str(e)}, 400)
                return
            if "name" in json_input and "email" in json_input:
                add_admin = False
                if "admin" in json_input and json_input["admin"]:
                    add_admin = True
                try:
                    returned_key = add_user(json_input,add_admin)
                except Exception, e:
                    self.response_handler({"message": "Something went wrong", "error": str(e)}, 500)
                    return
                if add_admin:
                    self.response_handler({"message": "Admin User Added Successfully!", "id": returned_key.urlsafe()})
                else:
                    self.response_handler({"message": "User Added Successfully!", "id": returned_key.urlsafe()})
            else:
                self.response_handler({"message": "Name and/or email missing"}, 400)
        else:
            self.response_handler({"message": "User is not admin"}, 401)
        return

    def put(self,**kwargs):
        user_email = users.get_current_user().email()
        logging.info("Request raised by : %s",user_email)

        if UserDetails.is_user_admin(user_email):
            try:
                json_input = json.loads(self.request.body)
            except Exception,e:
                self.response_handler({"message": "No input received or invalid input", "error":str(e)}, 400)
                return
            try:
                user_obj = ndb.Key(urlsafe=kwargs["userId"]).get()
            except:
                self.response_handler({"message": "Invalid user id"}, 400)
                return
            try:
                update_user(json_input,user_obj)
            except Exception, e:
                self.response_handler({"message": "Something went wrong", "error": str(e)}, 500)
                return
            self.response_handler({"message": "User Updated Successfully!"})
        else:
            self.response_handler({"message": "User is not admin"},401)
        return

    def delete(self, **kwargs):
        user_email = users.get_current_user().email()
        logging.info("Request raised by : %s",user_email)

        if UserDetails.is_user_authenticated(user_email):
            try:
                user_key = ndb.Key(urlsafe=kwargs["userId"])
            except:
                self.response_handler({"message": "Invalid user id"}, 400)
                return
            user_key.delete()
            self.response_handler({"message": "User Deleted Successfully!"})
        else:
            self.response_handler({"message": "User is not admin"}, 401)
        return

    def response_handler(self, response_dict=None, code=200):
        self.response.set_status(code)
        self.response.out.write(json.dumps(response_dict))

class FirstUser(webapp2.RequestHandler):
    def get(self):
        if not UserDetails.first_user_exists():
            try:
                user_obj = users.get_current_user()
                user_email = user_obj.email()
                logging.info("Request raised by : %s",user_email)

                json_input = dict(self.request.params) if self.request.params else {}
                if "name" not in json_input:
                    json_input["name"] = user_obj.nickname()
                json_input["email"] = user_email
                add_user(json_input,True)
                time.sleep(0.1)
            except Exception, e:
                self.response_handler({ "message": "Something went wrong", "error":str(e)}, 500)
                return
            self.redirect('/')
        else:
            self.response_handler({ "message": "First Admin already exists"}, 403)
        return

    def response_handler(self, response_dict=None, code=200):
        self.response.set_status(code)
        self.response.out.write(json.dumps(response_dict))

class UsersList(webapp2.RequestHandler):
    def get(self):
        user_email = users.get_current_user().email()
        logging.info("Request raised by : %s",user_email)

        if UserDetails.is_user_admin(user_email):
            params = dict(self.request.params)
            try:
                type = params["type"]
            except:
                self.response_handler({ "message": "Type missing for admin/user"},400)
                return
            cursor = ndb.Cursor(urlsafe=params["cursor"]) if "cursor" in params else None
            limit = params["limit"] if "limit" in params else 10

            try:
                query_results, cursor, more = UserDetails.get_users_for_type(type,cursor,limit)
                return_list = serialise_users_list(query_results)
                if cursor:
                    cursor = cursor.urlsafe()
            except Exception, e:
                self.response_handler({"message": "Something went wrong", "error": str(e)}, 500)
                return
            self.response_handler({"usersList": return_list,"cursor":cursor,"more":more})
        else:
            self.response_handler({"message": "You are not authorised"}, 401)
        return

    def response_handler(self,response_dict=None,code=200):
        self.response.set_status(code)
        self.response.out.write(json.dumps(response_dict))