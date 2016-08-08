from app.user.models_user import *
from google.appengine.ext import ndb

def add_user(json_input,admin_user):
    new_user_entry = UserDetails()
    new_user_entry.name = json_input["name"]
    new_user_entry.email = json_input["email"]
    new_user_entry.admin = admin_user
    returned_key = new_user_entry.put()
    return returned_key

def update_user(json_input,user_obj):
    for key, value in json_input.iteritems():
        setattr(user_obj, key, value)
    user_obj.put()

def serialise_users_list(query_results):
    users_list = []
    for a_result in query_results:
        return_dict = {}
        return_dict["name"] = a_result.name
        return_dict["email"] = a_result.email
        return_dict["id"] = a_result.key.urlsafe()
        users_list.append(return_dict)
    return users_list
