import webapp2
from google.appengine.api import users

class Logout(webapp2.RequestHandler):
    def get(self):
        logout_url = users.create_logout_url('/')
        self.redirect(str(logout_url))
        return