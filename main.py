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
    token = get_token(client_id, tenant_id, refresh_token)
    headers = {'Authorization': "Bearer {}".format(token['accessToken'])}
    print("This is the header: %s" % headers)
    response = requests.get("https://api.powerbi.com/v1.0/myorg/datasets", headers=headers)
    
    #response = requests.get("https://api.powerbi.com/v1.0/myorg/datasets", headers=headers)
    print(response.status_code)
    print(response.reason)
    return jsonify(response.json())

@app.route('/post_data', methods=['GET','POST'])
def posting_data():
    
    test_data =   {
    "name": "SalesMarketing",
    "defaultMode": "Push",
    "tables": [
    {
      "name": "Product",
      "columns": [
        {
          "name": "ProductID",
          "dataType": "Int64"
        },
        {
          "name": "Name",
          "dataType": "string"
        },
        {
          "name": "Category",
          "dataType": "string"
        },
        {
          "name": "IsCompete",
          "dataType": "bool"
        },
        {
          "name": "ManufacturedOn",
          "dataType": "DateTime"
        }
      ]
    }
    ]
  }
    token = get_token(client_id, tenant_id,refresh_token)
    headers = {'Authorization': "Bearer {}".format(token['accessToken'])}
    response = requests.post("https://api.powerbi.com/v1.0/myorg/datasets", headers=headers, json=test_data)
    print(response.status_code)
    print (response.content)
    #return jsonify(test_data)
    return jsonify(response.json())

if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)
