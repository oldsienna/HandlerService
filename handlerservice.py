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
    if not request.json or not 'name' in request.json:
        abort(400)
    handler = {
        'registration_id': request.json['registration_id'],
        'name': request.json['name'],
        'description': request.json.get('description', ""),
        'handler_id': request.json.get('handler_id'),
        'pedigree': request.json.get('pedigree'),
        'reg_status': False,
        'vacc_status': False
    }
    id = models.new_handler(handler)
    handler['id'] = id

    return jsonify( { 'handler': handler } ), 201

# Service Call for updating a handler
@app.route('/api/v1.0/handler/<string:handler_id>', methods = ['PUT'])
def update_handler(handler_id):
    handler = models.get_handler(handler_id)
    if len(handler) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'name' in request.json and type(request.json['name']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'registration_id' in request.json and type(request.json['registration_id']) is not unicode:
        abort(400)
    if 'handler_id' in request.json and type(request.json['handler_id']) is not int:
        abort(400)
    if 'reg_status' in request.json and type(request.json['reg_status']) is not bool:
        abort(400)
    if 'vacc_status' in request.json and type(request.json['vacc_status']) is not bool:
        abort(400)
    if 'pedigree' in request.json and type(request.json['pedigree']) is not unicode:
        abort(400)
    handler['name'] = request.json.get('name', handler['name'])
    handler['registration_id'] = request.json.get('registration_id', handler['registration_id'])
    handler['description'] = request.json.get('description', handler['description'])
    handler['handler_id'] = request.json.get('handler_id', handler['handler_id'])
    handler['reg_status'] = request.json.get('reg_status', handler['reg_status'])
    handler['vacc_status'] = request.json.get('vacc_status', handler['vacc_status'])
    models.update_handler(handler)

    return jsonify( { 'handler': handler } )

# Service Call for deleting a handler
@app.route('/api/v1.0/handler/<string:handler_id>', methods = ['DELETE'])
def delete_handler(handler_id):
    handler = models.get_handler(handler_id)
    if len(handler) == 0:
        abort(404)
    models.delete_handler(handler_id)
    return jsonify( { 'result': True } )

# Initialise DB before starting web service
models.init_db()
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', '5000')))
