from flask import Flask, request, jsonify
import json
import requests
from authentification.create_jwt import *

## Setting helpers
application_id = "8df57daa-57e6-4044-9d3f-33aee3171de8"
application_secret = "AXov1dtKsZjakaxr0oh3zUiyVsRD3vwfBBgKwTSc3dE"
tenant_id = ""
##

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
    headers = make_headers(application_id, application_secret, user_id, user_password)
    response = requests.get("https://api.powerbi.com/v1.0/myorg/datasets/", headers=headers).json()
    return response

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