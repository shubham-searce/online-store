import webapp2
import json
from google.appengine.api import users
from app.user.models_user import *

class Welcome(webapp2.RequestHandler):
    def get(self):
        user_obj = users.get_current_user()
        user_email = user_obj.email()
        try:
            get_user = UserDetails.get_authenticated_user(user_email)
        except Exception, e:
            self.response_handler({"message": "Something went wrong", "error": "problem while searching" + str(e)}, 500)
            return
        if get_user:
            self.response_handler({"message": "Welcome "+get_user.name+", You are authorised!"})
        else:
            self.response_handler({"message": "Sorry. You are not authorised!"}, 401)
        return

    def response_handler(self, response_dict=None, code=200):
        self.response.set_status(code)
        self.response.out.write(json.dumps(response_dict))