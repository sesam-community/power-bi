from flask import Flask, request, jsonify
import json
from authentification.create_jwt import get_token
from processing.powerBi import *
#from authentification.set_config import *
import sys
import os
import time


app           = Flask(__name__)

def get_env(var):
    envvar = None
    if var.upper() in os.environ:
        envvar = os.environ[var.upper()]
    return envvar

Sesam_headers   = {'Authorization': "Bearer {}".format(get_env('SESAM-JWT'))}
token           = get_token(get_env('PBI-CLIENT-ID'), get_env('TENANT-ID'), get_env('PBI-REFRESH-TOKEN'))
Powerbi_headers = {'Authorization': "Bearer {}".format(token['accessToken'])}
powerbi_url     = "https://api.powerbi.com/v1.0/myorg/groups/%s/datasets" % get_env('WORKSPACE-ID')
workspace_id    = get_env("WORKSPACE-ID")

print(9)
@app.route('/get_sesam/<node_id>/<pipe_name>', methods=['POST'])
def get_sesam(node_id, pipe_name):

    print(10)
    entities = request.get_json()#"https://%s.sesam.cloud/api/pipes/%s/entities" %(node_id, pipe_name), headers=Sesam_headers)
    schema   = requests.get("https://%s.sesam.cloud/api/pipes/%s/generate-schema-definition" %(node_id, pipe_name), headers = Sesam_headers).json()
    dataset                 = setup_dataset(pipe_name)
    populated_dataset, keys = add_columns(dataset, entities, schema)
    rows                    = add_rows(entities, populated_dataset, keys)

    # If the dataset from Sesam already exists in Power BI, the Power BI dataset gets updated
    current_datasets                        = get_powerbi(workspace_id)
    update_rows, update_columns, dataset_id = check_dataset_status(current_datasets, entities, pipe_name)


    if update_rows:
        delete_powerbi_rows(dataset_id, pipe_name)
    else:
        if update_columns:
            delete_powerbi_columns(dataset_id)
            post_powerbi_columns(populated_dataset)
        else: # if new_dataset
            post_powerbi_columns(populated_dataset)
            response = get_powerbi(workspace_id)
        response    = get_powerbi(workspace_id)
        dataset_id  = find_dataset_id(response, pipe_name)

    # Posting the entities
    post_powerbi_rows(dataset_id, pipe_name, rows)
    response        = get_powerbi(workspace_id, '/' + dataset_id)
    return jsonify(response.json())



@app.route('/post_powerbi_rows', methods=['POST'])
def post_powerbi_rows(dataset_id, pipe_name, data):
    requests.post(powerbi_url + "/%s/tables/%s/rows" % (dataset_id, pipe_name), headers=Powerbi_headers, json=data)

@app.route('/post_powerbi_columns', methods=['POST'])
def post_powerbi_columns(data):
    requests.post(powerbi_url, headers=Powerbi_headers, json=data)

@app.route('/update_powerbi_rows', methods=['DELETE'])
def delete_powerbi_rows(dataset_id, table_name):
    requests.delete(powerbi_url + '/' + dataset_id + '/tables/%s/rows' %table_name, headers=Powerbi_headers)

@app.route('/update_powerbi_columns', methods=['DELETE'])
def delete_powerbi_columns(dataset_id):
    requests.delete(powerbi_url + '/' + dataset_id, headers=Powerbi_headers)
    

@app.route('/get_powerbi', methods=['GET'])
def get_powerbi(workspace_id, dataset_id = str()):
    powerbi_url       = "https://api.powerbi.com/v1.0/myorg/groups/%s/datasets" % workspace_id
    response    = requests.get(powerbi_url + dataset_id, headers=Powerbi_headers)
    return response

if __name__ == '__main__':


    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
