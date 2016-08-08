import webapp2
from app.user.urls_user import url_patterns_user
from app.store.urls_store import url_patterns_store
from app.welcome.urls_welcome import url_patterns_welcome
from app.logout.urls_logout import url_patterns_logout


url_patterns = list()
url_patterns.extend(url_patterns_user)
url_patterns.extend(url_patterns_store)
url_patterns.extend(url_patterns_welcome)
url_patterns.extend(url_patterns_logout)


application = webapp2.WSGIApplication(url_patterns, debug=True)
