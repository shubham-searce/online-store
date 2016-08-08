from app.user.views_user import *
import webapp2

url_patterns_user = [('/adduser', UserHandler),
                     webapp2.Route('/edituser/<userId>', UserHandler),
                     webapp2.Route('/deleteuser/<userId>', UserHandler),
                     ('/firstuser', FirstUser),
                     ('/userlist', UsersList)]