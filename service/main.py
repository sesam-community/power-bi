from flask import Flask, request, jsonify
import logging
import requests
import json
from authentification.create_jwt import get_token
from error_methods import *
from processing.powerBi import *
import os

logger = logging.getLogger('powerbi-microservice')
format_string = '%(asctime)s - %(lineno)d - %(levelname)s - %(message)s'
# Log to stdout
stdout_handler = logging.StreamHandler()
stdout_handler.setFormatter(logging.Formatter(format_string))
logger.addHandler(stdout_handler)
logger.setLevel(logging.INFO)

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

print(get_env('PBI-CLIENT-ID'))
print(get_env('TENANT-ID'))
print(get_env('PBI-REFRESH-TOKEN'))
#print(get_env(''))
ss
@app.route('/get_sesam/<node_id>/<pipe_name>', methods=['POST'])
def main_func(node_id, pipe_name):
    entities = request.get_json()

    if max_entities_exceeded(entities):
        logger.error("The number of entites (%i) exceeds the Power BI max rows per post limitation. Set the Sesam batch_size to max 10000" %len(entities)) 

    args     = request.args
    response = requests.get("https://%s.sesam.cloud/api/pipes/%s/generate-schema-definition" %(node_id, pipe_name), headers = Sesam_headers)
    if response.status_code == 200:
        logger.debug("Sent get request for schema to node id %s, pipe %s in Sesam" %(node_id, pipe_name))
    else:
        logger.warning("Failed to send get request for schema to node id %s, pipe %s in Sesam" %(node_id, pipe_name))

    schema   = response.json()

    try: 
        schema[0]
    except KeyError:
        logger.warning("Failed to generate correct schema from Sesam")
    except IndexError:
        logger.warning("Failed to generate correct schema from Sesam")

    dataset                 = setup_dataset(pipe_name)
    populated_dataset, keys = add_columns(dataset, schema)
    rows                    = add_rows(entities, populated_dataset, keys)

    if max_properties_exceeded(keys):
        logger.error("The number of properties (%i) exceeds the Power BI max columns limitation of 75" %len(keys))
    
    # If the dataset from Sesam already exists in Power BI, the Power BI dataset gets updated
    current_datasets               = get_powerbi()
    create_new_dataset, dataset_id = check_dataset_status(current_datasets, pipe_name)

    try:
        args['is_first']
        if create_new_dataset:
            create_powerbi_dataset(populated_dataset, pipe_name)
            current_datasets                        = get_powerbi()
            create_new_dataset, dataset_id = check_dataset_status(current_datasets, pipe_name)
        else:
            logger.info("The MS does not support a different amount of properties between the new dataset and the old one. If so, then delete the old dataset in Power BI.")
            delete_powerbi_rows(dataset_id, pipe_name)

        post_powerbi_rows(dataset_id, pipe_name, rows)

    except KeyError:
        post_powerbi_rows(dataset_id, pipe_name, rows)

    # Posting the entities
    response        = get_powerbi('/' + dataset_id)
    try: 
        args['is_last']
        return("Success in sending data from Sesam into Power BI.")
    except KeyError:
        return ("Sending batch %i." % int(args['request_id']))

@app.route('/delete_powerbi_rows', methods=['DELETE'])
def delete_powerbi_rows(dataset_id, pipe_name):
    response = requests.delete(powerbi_url + "/%s/tables/%s/rows" % (dataset_id, pipe_name), headers=Powerbi_headers)
    if response.status_code == 200:
        logger.debug("Deleted the excisting rows in workspace %s, dataset %s, table %s in Power BI" %(workspace_id, pipe_name, pipe_name))
    else:
        logger.warning("Failed to deleted the excisting rows in workspace %s, dataset %s, table %s in Power BI" %(workspace_id, pipe_name, pipe_name))

@app.route('/post_powerbi_rows', methods=['POST'])
def post_powerbi_rows(dataset_id, pipe_name, data):
    response = requests.post(powerbi_url + "/%s/tables/%s/rows" % (dataset_id, pipe_name), headers=Powerbi_headers, json=data)
    if response.status_code == 200:
        logger.debug("Posted rows into workspace %s, dataset %s, table %s in Power BI" %(workspace_id, pipe_name, pipe_name))
    else:
        logger.warning("Failed to post rows into workspace %s, dataset %s, table %s in Power BI" %(workspace_id, pipe_name, pipe_name))

@app.route('/create_powerbi_dataset', methods=['PUT'])
def create_powerbi_dataset(data, pipe_name):
    response = requests.post(powerbi_url,  headers=Powerbi_headers, json=data)

    if response.status_code == 201:
        logger.debug("Created dataset %s, table %s in workspace %s in Power BI" %(pipe_name, pipe_name, workspace_id))
    else:
        logger.warning("Failed to create dataset into dataset %s, table %s in workspace %s in Power BI" %(pipe_name, pipe_name, workspace_id))

@app.route('/get_powerbi', methods=['GET'])
def get_powerbi(dataset_id = str()):
    response    = requests.get(powerbi_url + dataset_id, headers=Powerbi_headers)
    if response.status_code == 200:
        logger.debug("Sent get request to workspace %s, dataset id %s in Power BI" %(workspace_id, dataset_id))
    else:
        logger.warning("Failed to send get request to workspace %s, dataset id %s in Power BI" %(workspace_id, dataset_id))
    return response

if __name__ == '__main__':

    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)