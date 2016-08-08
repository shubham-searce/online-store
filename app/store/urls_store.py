from app.store.views_store import *
import webapp2

url_patterns_store = [('/product', Store),
                      ('/product/search', StoreSearch),
                      webapp2.Route('/product/<productId>', Store)]