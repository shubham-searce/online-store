from app.user.views_user import *
import webapp2

url_patterns_user = [('/user', UserHandler),
                     webapp2.Route('/user/<userId>', UserHandler),
                     ('/firstuser', FirstUser),
                     ('/userlist', UsersList)]