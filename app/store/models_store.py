from google.appengine.ext import ndb

class Product(ndb.Model):
    name = ndb.StringProperty(required=True)
    productId = ndb.StringProperty(required=True)
    description = ndb.TextProperty()
    category = ndb.StringProperty()
    manufacturer = ndb.StringProperty()

    addedOn = ndb.DateTimeProperty(auto_now_add=True)
    addedBy = ndb.StringProperty()
    modifiedOn = ndb.DateTimeProperty(auto_now=True)
    modifiedBy = ndb.StringProperty()
