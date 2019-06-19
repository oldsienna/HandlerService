#!flask/bin/python
import os
import pymongo
import models
from flask import Flask, jsonify, abort, request, make_response, url_for

app = Flask(__name__)

# Error Handler for 400: Bad Request
@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)

# Error Handler for 404: Not Found 
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)
    
# Service Call for retrieving list of handlers
@app.route('/api/v1.0/handlers', methods = ['GET'])
def get_handlers():
    handlers = models.get_handlers()
    return jsonify( { 'handlers': handlers } ), 201

# Service Call for retrieving a handler's details using id
@app.route('/api/v1.0/handler/<string:handler_id>', methods = ['GET'])
def get_handler(handler_id):
    handler = models.get_handler(handler_id)

    if not handler:
        # No handler with that id found
        abort(404)

    return jsonify( { 'handler': handler })

# Service Call for creating a new handler
@app.route('/api/v1.0/handler', methods = ['POST'])
def create_handler():
    # Check for JSON input and mandatory email, first_name and last_name
    if not request.json or not 'email' in request.json or not 'first_name' in request.json or not 'last_name' in request.json:
        abort(400)

    handler = {
        'email': request.json['email'],
        'first_name': request.json['first_name'],
        'last_name': request.json['last_name'],
        'street': request.json.get('street', None),
        'suburb': request.json.get('suburb', None),
        'state': request.json.get('state', None),
        'zip_code': request.json.get('zip_code', None),
        'phone': request.json.get('phone', None)
    }

    # Clean up fields if they exist
    if not (handler['email'] is None)      : handler['email'] = handler['email'].strip().lower()
    if not (handler['first_name'] is None) : handler['first_name'] = handler['first_name'].strip().capitalize()
    if not (handler['last_name'] is None)  : handler['last_name'] = handler['last_name'].strip().capitalize()
    if not (handler['street'] is None)     : handler['street'] = handler['street'].strip()
    if not (handler['suburb'] is None)     : handler['suburb'] = handler['suburb'].strip().capitalize()
    if not (handler['state'] is None)      : handler['state'] = handler['state'].strip().upper()
    if not (handler['zip_code'] is None)   : handler['zip_code'] = handler['zip_code'].strip()
    if not (handler['phone'] is None)      : handler['phone'] = handler['phone'].strip()

    id = models.new_handler(handler)
    handler['id'] = id

    return jsonify( { 'handler': handler } ), 201

# Service Call for updating a handler
@app.route('/api/v1.0/handler/<string:handler_id>', methods = ['PUT'])
def update_handler(handler_id):
    handler = models.get_handler(handler_id)
    # Exhaustive checking of the input arguments before passing to DB
    if len(handler) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'email' in request.json and type(request.json['email']) is not unicode:
        abort(400)
    if 'first_name' in request.json and type(request.json['first_name']) is not unicode:
        abort(400)
    if 'last_name' in request.json and type(request.json['last_name']) is not unicode:
        abort(400)
    if 'street' in request.json and type(request.json['street']) is not unicode:
        abort(400)
    if 'suburb' in request.json and type(request.json['suburb']) is not unicode:
        abort(400)
    if 'state' in request.json and type(request.json['state']) is not unicode:
        abort(400)
    if 'zip_code' in request.json and type(request.json['zip_code']) is not unicode:
        abort(400)
    if 'phone' in request.json and type(request.json['phone']) is not unicode:
        abort(400)
    
    handler['email'] = request.json.get('email', handler['email'])
    handler['first_name'] = request.json.get('first_name', handler['first_name'])
    handler['last_name'] = request.json.get('last_name', handler['last_name'])
    handler['street'] = request.json.get('street', handler['street'])
    handler['suburb'] = request.json.get('suburb', handler['suburb'])
    handler['state'] = request.json.get('state', handler['state'])
    handler['zip_code'] = request.json.get('zip_code', handler['zip_code'])
    handler['phone'] = request.json.get('phone', handler['phone'])
    models.update_handler(handler)

    return jsonify( { 'handler': handler } )

# Service Call for deleting a handler
@app.route('/api/v1.0/handler/<string:handler_id>', methods = ['DELETE'])
def delete_handler(handler_id):
    handler = models.get_handler(handler_id)
    if handler is None:
        abort(404)
    models.delete_handler(handler_id)
    return jsonify( { 'result': True } )

# Service Call for finding handlers by criteria (similar to Update Handler method)
# Accepts a single field or multiple fields which are then AND'ed
@app.route('/api/v1.0/search', methods = ['PUT'])
def search():
    if not request.json:
        abort(400)
    criteria = {}

    if 'email' in request.json:
        email = str(request.json['email']).strip().lower()
        criteria['email'] = email

    if 'last_name' in request.json:
        last_name = str(request.json['last_name']).strip().capitalize()
        criteria['last_name'] = last_name

    if 'zip_code' in request.json:
        zip_code = str(request.json['zip_code']).strip()
        criteria['zip_code'] = zip_code

    handler = models.search(criteria)
    return jsonify( {'handlers': handler} )

# Initialise DB before starting web service
models.init_db()
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', '5000')))