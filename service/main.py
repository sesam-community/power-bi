from flask import Flask, request, jsonify
import logging
import requests
import json
from authentification.create_jwt import get_token
from processing.powerBi import *
import os

app           = Flask(__name__)

def get_env(var):
    envvar = None
    if var.upper() in os.environ:
        envvar = os.environ[var.upper()]
    return envvar

def check_dataset_status(current_datasets, pipe_name):
    create_new_dataset = dataset_id = True
    for dataset_ in current_datasets.json()['value']:
        if dataset_['name'] == pipe_name:
            create_new_dataset = False
            dataset_id = dataset_['id']

    return create_new_dataset, dataset_id


Sesam_headers   = {'Authorization': "Bearer {}".format(get_env('SESAM-JWT'))}
token           = get_token(get_env('PBI-CLIENT-ID'), get_env('TENANT-ID'), get_env('PBI-REFRESH-TOKEN'))
Powerbi_headers = {'Authorization': "Bearer {}".format(token['accessToken'])}
powerbi_url     = "https://api.powerbi.com/v1.0/myorg/groups/%s/datasets" % get_env('WORKSPACE-ID')
workspace_id    = get_env("WORKSPACE-ID")

@app.route('/get_sesam/<node_id>/<pipe_name>', methods=['POST'])
def main_func(node_id, pipe_name):
    entities = request.get_json()
    args = request.args
    schema   = requests.get("https://%s.sesam.cloud/api/pipes/%s/generate-schema-definition" %(node_id, pipe_name), headers = Sesam_headers).json()
    dataset                 = setup_dataset(pipe_name)
    populated_dataset, keys = add_columns(dataset, schema)
    rows                    = add_rows(entities, populated_dataset, keys)

    # If the dataset from Sesam already exists in Power BI, the Power BI dataset gets updated
    current_datasets                        = get_powerbi(workspace_id)
    create_new_dataset, dataset_id = check_dataset_status(current_datasets, pipe_name)


    try:
        args['is_first']
        if create_new_dataset:
            create_powerbi_dataset(dataset_id, populated_dataset)
            current_datasets                        = get_powerbi(workspace_id)
            create_new_dataset, dataset_id = check_dataset_status(current_datasets, pipe_name)
        else:
            delete_powerbi_rows(dataset_id, pipe_name)

        post_powerbi_rows(dataset_id, pipe_name, rows)

    except KeyError:
        post_powerbi_rows(dataset_id, pipe_name, rows)

    # Posting the entities
    response        = get_powerbi(workspace_id, '/' + dataset_id)
    try: 
        args['is_last']
        app.logger.info("Success in sending data from Sesam into Power BI.")
    except KeyError:
        app.logger.info("Sending batch %i." % int(args['request_id']))
    return jsonify(response.status_code)

@app.route('/delete_powerbi_rows', methods=['DELETE'])
def delete_powerbi_rows(dataset_id, pipe_name):
    requests.delete(powerbi_url + "/%s/tables/%s/rows" % (dataset_id, pipe_name), headers=Powerbi_headers)

@app.route('/post_powerbi_rows', methods=['POST'])
def post_powerbi_rows(dataset_id, pipe_name, data):
    requests.post(powerbi_url + "/%s/tables/%s/rows" % (dataset_id, pipe_name), headers=Powerbi_headers, json=data)

@app.route('/create_powerbi_dataset', methods=['PUT'])
def create_powerbi_dataset(data):
    requests.post("https://api.powerbi.com/v1.0/myorg/groups/%s/datasets" % (workspace_id),  headers=Powerbi_headers, json=data)

@app.route('/get_powerbi', methods=['GET'])
def get_powerbi(workspace_id, dataset_id = str()):
    response    = requests.get(powerbi_url + dataset_id, headers=Powerbi_headers)
    return response

if __name__ == '__main__':
    logger = logging.getLogger('powerbi-microservice')
    format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    # Log to stdout
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(stdout_handler)

    logger.setLevel(logging.DEBUG)
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)