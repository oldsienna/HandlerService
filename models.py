#!/usr/bin/env python

#########################################################
# This is the functional processing file.
# It contains the DB connections, queries and processes
#########################################################

# Import modules required for app
import os, time, json, re
from pymongo import MongoClient
from bson.objectid import ObjectId

def db_conn():
    # Check if user defined environment variable exists
    if "DB_URI" in os.environ:
        DB_ENDPOINT = MongoClient(os.environ['DB_URI'])
        DB_NAME = os.environ['DB_Name']

	# Check if running in Pivotal Web Services with MongoDB service bound
    elif 'VCAP_SERVICES' in os.environ:
        VCAP_SERVICES = json.loads(os.environ['VCAP_SERVICES'])
        MONGOCRED = VCAP_SERVICES["mlab"][0]["credentials"]
        DB_ENDPOINT = MongoClient(MONGOCRED["uri"])
        DB_NAME = str(MONGOCRED["uri"].split("/")[-1])

    # Otherwise, assume running locally with local MongoDB instance
    else:
	    DB_ENDPOINT = MongoClient('127.0.0.1:27017')
	    DB_NAME = "Handlers"
    # Get database connection using database endpoint and name defined above
    global db
    db = DB_ENDPOINT[DB_NAME]

def init_db():
    db_conn() # Connect to database

# Create a new handler entry
def new_handler(handler):
    # If handler email already exists in the system then raise an error
    handler_exists = db.handler_details.find_one({'email': handler['email']})

    if not handler_exists:
        # Add handler to database
        return_code = 0
        _id = db.handler_details.insert({
                                    'email': handler['email'],
                                    'first_name': handler['first_name'],
                                    'last_name': handler['last_name'],
                                    'street': handler['street'],
                                    'suburb': handler['suburb'],
                                    'state': handler['state'],
                                    'zip_code': handler['zip_code'],
                                    'phone': handler['phone']
                                    })
    # Return the id of the newly created handler
	return str(_id)

# Retrieve a handler by id
def get_handler(handler_id):
    handler = db.handler_details.find_one({'_id': ObjectId(handler_id)})
    # Check if handler exists
    if handler:
        handler = {
            'id': handler_id,
            'email': handler.get('email'),
            'first_name': handler.get('first_name'),
            'last_name':handler.get('last_name'),
            'street': handler.get('street'),
            'suburb': handler.get('suburb'),
            'state': handler.get('state'),
            'zip_code': handler.get('zip_code'),
            'phone': handler.get('phone')
        }
        return handler
    else:
        return None

# Return an array of handler details, limited by max_number
def get_handlers(max_number = 10):
    handlers = []

    for handler in db.handler_details.find().sort("last_name", 1).limit(max_number):
        handler = {
            'id': str(handler.get('_id')),
            'email': handler.get('email'),
            'first_name': handler.get('first_name'),
            'last_name': handler.get('last_name'),
            'street': handler.get('street'),
            'suburb': handler.get('suburb'),
            'state': handler.get('state'),
            'zip_code': handler.get('zip_code'),
            'phone': handler.get('phone')
        }
        handlers.append(handler)

    return handlers

# Update a handler record
def update_handler(handler):
    # Update handler fields if present
    db.handler_details.update_one({'_id': ObjectId(handler['id'])},
                    { "$set" :
                            { 
                                'email': handler.get('email'),
                                'first_name': handler['first_name'],
                                'last_name': handler['last_name'],
                                'street': handler['street'],
                                'suburb': handler['suburb'],
                                'state': handler['state'],
                                'zip_code': handler['zip_code'],
                                'phone': handler['phone'] 
                            }
                    },
                    upsert=True)
    return

# Delete a handler by id
def delete_handler(handler_id):
    db.handler_details.delete_one({'_id': ObjectId(handler_id)})