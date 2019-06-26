from flask import Flask, request, jsonify
import json
import requests
from authentification.create_jwt import get_token
from authentification.auth_helpers import *
from sesam.getting_sesam_data import get_sesam_data
from processing.powerBi import make_PowerBi_json

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
    token = get_token(client_id, client_secret, tenant_id)
    headers = {'Authorization': "Bearer {}".format(token['accessToken'])}
    print("This is the headers: %s" % headers)
    response = requests.get("https://api.powerbi.com/v1.0/myorg/datasets", headers=headers)
    print(response.status_code)
    print(response.reason)
    return jsonify(response.json())

@app.route('/post_data', methods=['GET','POST'])
def posting_data():
    
    sesam_data =   {
       'id': 1,
       'Username': u'Unjudosely',
       'Orders': u'Thinkpad',
       'TotalSum': 8000
    }
    token = get_token(client_id, client_secret, tenant_id)
    headers = {'Authorization': "Bearer {}".format(token['accessToken'])}
    response = requests.post("https://api.powerbi.com/v1.0/myorg/datasets", headers=headers, data=sesam_data)
    print(response.status_code)
    print(response.reason)
    
    pipe_data = get_sesam_data(sesam_jwt, start_endpoint).json()
    powerBi_json = make_PowerBi_json(pipe_data)
    #return jsonify(pipe_data)
    return jsonify(response.json())

if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)