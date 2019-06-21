from flask import Flask, request, jsonify
import json
import requests
from authentification.create_jwt import *
from authentification.auth_helpers import *

app = Flask(__name__)

@app.route('/')
def index():
    output = {
        'service': 'Power BI Connector',
        'remote_addr': request.remote_addr
    }
    return jsonify(output)

@app.route('/get_data', methods=['GET'])
def getting_data():
    headers = get_token(client_id, client_secret, tenant_id)
    response = requests.get("https://api.powerbi.com/v1.0/myorg/datasets/", headers=headers)
    return jsonify(response)

@app.route('/post_data', methods=['GET','POST'])
def posting_data():
    output = {
        'Erik': 'Does something magical!'
    }
    return jsonify(output)

if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)