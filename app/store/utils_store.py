from app.store.models_store import Product
from google.appengine.api import search
from google.appengine.ext import ndb
import re
import logging
import datetime

def add_product_entry(entry_json,user_email):
    new_product_entry = Product()
    new_product_entry.name = entry_json["name"]
    new_product_entry.description = entry_json["description"] if "description" in entry_json else ""
    new_product_entry.category = entry_json["category"] if "category" in entry_json else ""
    new_product_entry.productId = entry_json["productId"]
    new_product_entry.manufacturer = entry_json["manufacturer"] if "manufacturer" in entry_json else "Unknown"
    new_product_entry.addedBy = user_email
    returned_key = new_product_entry.put()
    returned_key_urlsafe = returned_key.urlsafe()
    create_product_document(new_product_entry,returned_key_urlsafe)
    return returned_key_urlsafe

def create_product_document(entry_obj,entry_id):
    bad_characters_in_document_regx = re.compile('[^a-zA-z0-9_+\. ]')
    document_fields = {"TextField":{"name":tokenize_product_detail(str(bad_characters_in_document_regx.sub('',entry_obj.name).lower())),
                                    "productId": tokenize_product_detail(
                                        str(bad_characters_in_document_regx.sub('', entry_obj.productId).lower())),
                                    "category":str(bad_characters_in_document_regx.sub('',entry_obj.category).lower()),
                                    "description":str(bad_characters_in_document_regx.sub('',entry_obj.description.lower())),
                                    "manufacturer":str(bad_characters_in_document_regx.sub('',entry_obj.manufacturer.lower()))},
                       "NumberField":{"addedOn":totimestamp(entry_obj.addedOn),
                                    "modifiedOn":totimestamp(entry_obj.modifiedOn)}}
    logging.info(document_fields)
    document_obj = search.Document(doc_id=entry_id, fields=create_document_fields(document_fields))
    index = search.Index(name='Store')
    logging.info(index)
    index.put(document_obj)

def tokenize_product_detail(product_detail):
    a = []
    length = len(product_detail)
    for x in range(1,length+1):
        a.append(product_detail[0:x])
    str = ", ".join(a)
    return str

def totimestamp(dt, epoch=datetime.datetime(1970,1,1)):
    td = dt - epoch
    return td.total_seconds()

def create_document_fields(search_fields_dict):
    document_fields = []
    for a_key in search_fields_dict:
        for field_name in search_fields_dict[a_key]:
            document_fields.append(getattr(search, a_key)(name=field_name, value=search_fields_dict[a_key][field_name]))
    return document_fields

def update_product_entry(entry_obj,json_input, user_email):
    for key,value in json_input.iteritems():
        setattr(entry_obj,key,value)
    entry_obj.modifiedBy = user_email
    returned_key = entry_obj.put()
    returned_key_urlsafe = returned_key.urlsafe()
    create_product_document(entry_obj,returned_key_urlsafe)

def create_query_string(params_dict):
    bad_characters_in_document_regx = re.compile('[^a-zA-z0-9_+\. ]')
    query_string = " "
    if "hasWords" in params_dict and params_dict["hasWords"]:
        query_string = bad_characters_in_document_regx.sub('',params_dict["hasWords"]).lower()
    if "name" in params_dict and params_dict["name"]:
        query_string += " " + "name=" + bad_characters_in_document_regx.sub('',params_dict["name"]).lower()
    if "productId" in params_dict and params_dict["productId"]:
        query_string += " " + "productId=" + bad_characters_in_document_regx.sub('',params_dict["productId"]).lower()
    if "category" in params_dict and params_dict["category"]:
        query_string += " " + "category=" + bad_characters_in_document_regx.sub('',params_dict["category"]).lower()
    if "manufacturer" in params_dict and params_dict["manufacturer"]:
        query_string += " " + "manufacturer=" + bad_characters_in_document_regx.sub('',params_dict["manufacturer"]).lower()
    return query_string

def serialise_document_objects(search_results):
    return_list = []
    for a_result in search_results:
        logging.info(a_result)
        return_dict = {}
        return_dict["id"] = a_result.doc_id
        product_obj = ndb.Key(urlsafe=return_dict["id"]).get()
        return_dict["name"] = product_obj.name
        return_dict["category"] = product_obj.category
        return_dict["description"] = product_obj.description
        return_dict["addedBy"] = product_obj.addedBy
        return_list.append(return_dict)
    return return_list

def create_sort_option(sort_dict, default_asc_value, default_desc_value):
    sort_expression = []

    sorting_order = sort_dict.iterkeys()
    for key in sorting_order:
        if sort_dict[key] == 'a':
            sort_expression.append(search.SortExpression(expression=key, direction=search.SortExpression.ASCENDING,
                                                        default_value=default_asc_value[key]))
        if sort_dict[key] == 'd':
            sort_expression.append(search.SortExpression(expression=key, direction=search.SortExpression.DESCENDING,
                                                        default_value=default_desc_value[key]))

    return search.SortOptions(sort_expression)