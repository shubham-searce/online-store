import webapp2
import json
from google.appengine.ext import ndb
from google.appengine.api import search, users
from app.user.models_user import *
from app.store.utils_store import *

class Store(webapp2.RequestHandler):
    def post(self):
        user_email = users.get_current_user().email()

        if UserDetails.is_user_authenticated(user_email):
            json_input = json.loads(self.request.body)

            if "name" and "productId" in json_input:
                try:
                    returned_key_urlsafe = add_product_entry(json_input,user_email)
                except Exception, e:
                    self.response_handler({"message": "Something went wrong", "error": str(e)}, 500)
                    return
                self.response_handler({"message": "Product Added Successfully!","id": returned_key_urlsafe})
            else:
                self.response_handler({"message": "Name and/or Product ID missing"}, 400)

        else:
            self.response_handler({"message": "User not authorised!"}, 401)
        return

    def put(self,**kwargs):
        user_email = users.get_current_user().email()

        if UserDetails.is_user_authenticated(user_email):
            try:
                json_input = json.loads(self.request.body)
            except:
                self.response_handler({"message": "No details sent"}, 400)
                return

            try:
                product_entry = ndb.Key(urlsafe=kwargs["productId"]).get()
            except:
                self.response_handler({"message": "Invalid Product id"}, 400)
                return

            try:
                update_product_entry(product_entry,json_input, user_email)
            except Exception, e:
                self.response_handler({"message": "Something went wrong", "error": str(e)}, 500)

            self.response_handler({"message": "Product Updated Successfully!"})

        else:
            self.response_handler({"message": "User not authorised!"},401)
        return

    def delete(self,**kwargs):
        user_email = users.get_current_user().email()

        if UserDetails.is_user_authenticated(user_email):

            try:
                product_key = ndb.Key(urlsafe=kwargs["productId"])
            except:
                self.response_handler({"message": "Invalid product id"}, 400)
                return

            try:
                product_key.delete()
                doc_index = search.Index(name="Store")
                doc_index.delete(kwargs["productId"])
            except Exception, e:
                self.response_handler({"message": "Something went wrong", "error": str(e)}, 500)
                return

            self.response_handler({"message": "Product Deleted Successfully!"})

        else:
            self.response_handler({"message": "User not authorised!"}, 401)
        return

    def response_handler(self, response_dict=None, code=200):
        self.response.set_status(code)
        self.response.out.write(json.dumps(response_dict))


class StoreSearch(webapp2.RequestHandler):

    default_asc_value = {'modifiedOn': totimestamp(datetime.datetime.now()),"name":"","addedOn":totimestamp(datetime.datetime.now())}
    default_desc_value = {'modifiedOn': totimestamp(datetime.datetime(1970,1,1,0,0,0)),"name":"","addedOn":totimestamp(datetime.datetime(1970,1,1,0,0,0))}

    def get(self):
        user_email = users.get_current_user().email()

        if UserDetails.is_user_authenticated(user_email):
            json_input = dict(self.request.params)

            sort_dict = json_input.get("sort", {})
            if "cursor" in json_input and json_input["cursor"] != "":
                cursor = search.Cursor(web_safe_string=json_input["cursor"])
            else:
                cursor = search.Cursor()
            limit = int(json_input["limit"]) if "limit" in json_input else 10

            try:
                query_string = create_query_string(json_input)
                sort_options = create_sort_option(sort_dict,self.default_asc_value,self.default_desc_value)
            except Exception, e:
                self.response_handler({"message": "Something went wrong", "error": "problem while creating sort option" + str(e)}, 500)
                return

            try:
                search_query = search.Query(query_string=query_string.strip(),
                                            options=search.QueryOptions(limit=limit, cursor=cursor,
                                                                        sort_options=sort_options))
                search_results = search.Index(name='Store').search(search_query)
                cursor = search_results.cursor
            except Exception, e:
                self.response_handler({"message": "Something went wrong", "error": "problem while searching" + str(e)}, 500)
                return

            try:
                return_list = serialise_document_objects(search_results)
            except Exception, e:
                self.response_handler({"message": "Something went wrong", "error": "problem while serialising objects" + str(e)}, 500)
                return

            self.response_handler({"data": return_list, "cursor": cursor.web_safe_string if cursor else ""})

        else:
            self.response_handler({"message": "User not authorised!"}, 401)
        return

    def response_handler(self, response_dict=None, code=200):
        self.response.set_status(code)
        self.response.out.write(json.dumps(response_dict))