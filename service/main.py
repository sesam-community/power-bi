from flask import Flask, request, jsonify
import logging
import requests
import adal
import json
from authentification.create_jwt import get_token
from error_methods import *
from processing.powerBi import *
import os
import time
from datetime import datetime
from config.make_config import *

def get_env(var):
    envvar = None
    if var.upper() in os.environ:
        envvar = os.environ[var.upper()]
    return envvar

logger = logging.getLogger('powerbi-microservice')
format_string = '%(asctime)s - %(lineno)d - %(levelname)s - %(message)s'
stdout_handler = logging.StreamHandler()
stdout_handler.setFormatter(logging.Formatter(format_string))
logger.addHandler(stdout_handler)
logger.setLevel(logging.INFO)


tenant_id         = get_env('TENANT-ID')
client_id         = get_env('PBI-CLIENT-ID')
refresh_token     = get_env('PBI-REFRESH-TOKEN')
workspace_id      = get_env("WORKSPACE-ID")
node_id           = get_env("SESAM-NODE-ID")
Sesam_headers     = {'Authorization': "Bearer {}".format(get_env('SESAM-JWT'))}
powerbi_url       = "https://api.powerbi.com/v1.0/myorg/groups/%s/datasets" % get_env('WORKSPACE-ID')
sesam_schema_pipe = "powerbi-schemas"


def schema_with_id(schema, dataset_id):
    remade_schema = {}
    remade_schema["_id"] = str(dataset_id)
    remade_schema['info'] = schema
    return remade_schema

def merge_schemas(old_schema, new_schema):
    merged_schema = new_schema
    for old_property in old_schema:
        if old_property.get('name') not in [new_property.get('name') for new_property in new_schema]:    
            merged_schema.append(old_property)
    return merged_schema

def find_old_schema(schemas, dataset_id):
    if len(schemas) == 0:
        return None
    for schema in schemas:
        if schema["_id"] == dataset_id:
            return schema.get('info')
    return None

def check_dataset_status(current_datasets, dataset_name):
    create_new_dataset = dataset_id = True
    for dataset_ in current_datasets.json()['value']:
        if dataset_['name'] == dataset_name:
            create_new_dataset = False
            dataset_id = dataset_['id']

    return create_new_dataset, dataset_id

def get_refresh_token():
    resource = 'https://analysis.windows.net/powerbi/api'
    auth_endpoint = 'https://login.microsoftonline.com'
    context = adal.AuthenticationContext('/'.join([auth_endpoint, tenant_id]))
    user_code_info = context.acquire_user_code(resource, client_id);
    logger.info(user_code_info.get('message'))
    res = context.acquire_token_with_device_code(resource, user_code_info, client_id)
    logger.info("This is your refresh token: %s" % res.get('refreshToken'))

def token_has_expired(token):
    if datetime.now() > datetime.strptime(token['expiresOn'], "%Y-%m-%d %H:%M:%S.%f"):
        return True
    else:
        return False

if refresh_token  == None: 
    get_refresh_token()
    time.sleep(6000)
    logger.info('Insert your refresh token into the Sesam system as instructed in the README and click "Save"')
else:
    token           = get_token(get_env('PBI-CLIENT-ID'), get_env('TENANT-ID'), get_env('PBI-REFRESH-TOKEN'))
    Powerbi_headers = {'Authorization': "Bearer {}".format(token['accessToken'])}


app             = Flask(__name__)

@app.route('/<pipe_name>/<dataset_name>/<table_name>', methods=['POST'])
def main_func(pipe_name, dataset_name, table_name):

    global token, Powerbi_headers
    if token_has_expired(token):
        token           = get_token(get_env('PBI-CLIENT-ID'), get_env('TENANT-ID'), get_env('PBI-REFRESH-TOKEN'))
        Powerbi_headers = {'Authorization': "Bearer {}".format(token['accessToken'])}

    entities = request.get_json()

    if max_entities_exceeded(entities):
        logger.error("The number of entites (%i) exceeds the Power BI max rows per post limitation. Set the Sesam batch_size to max 10000" %len(entities)) 

    args     = request.args
    # If the dataset from Sesam already exists in Power BI, the Power BI dataset gets updated
    current_datasets               = get_powerbi()
    create_new_dataset, dataset_id = check_dataset_status(current_datasets, dataset_name)
    



    try:
        args['is_first']
        new_schema = get_new_schema(node_id, pipe_name)

        try: 
            new_schema[0]

        except KeyError:
            logger.warning("Failed to generate correct new schema from Sesam")

        except IndexError:
            logger.warning("Failed to generate correct new schema from Sesam")

        schemas = get_old_schemas(node_id, sesam_schema_pipe)
        old_schema = find_old_schema(schemas, dataset_id)

        if old_schema == None:
            schema = new_schema
        else:
            schema = merge_schemas(old_schema, new_schema)
        os.environ['SESAM-SCHEMA'] = json.dumps(schema)

    except KeyError:
        schema = json.loads(get_env('SESAM-SCHEMA'))



    dataset                 = setup_dataset(dataset_name, table_name)
    populated_dataset, keys = add_columns(dataset, schema)
    rows                    = add_rows(entities, populated_dataset, keys)
    if max_properties_exceeded(keys):
        logger.error("The number of properties (%i) exceeds the Power BI max columns limitation of 75" %len(keys))
   
    try:
        args['is_first']
        if create_new_dataset:
            create_powerbi_dataset(populated_dataset, dataset_name, table_name)
            current_datasets               = get_powerbi()
            create_new_dataset, dataset_id = check_dataset_status(current_datasets, dataset_name)
            post_powerbi_rows(dataset_id, dataset_name, table_name, rows)
        else:
            update_powerbi_columns(dataset_id, dataset_name, table_name, populated_dataset['tables'][0])
            delete_powerbi_rows(dataset_id, dataset_name, table_name)
            post_powerbi_rows(dataset_id, dataset_name, table_name, rows)

    except KeyError:
        post_powerbi_rows(dataset_id, dataset_name, table_name, rows)

    # Posting the entities
    response        = get_powerbi('/' + dataset_id)

    try:
        args['is_first']
        update_schemas(node_id, sesam_schema_pipe, schemas, schema_with_id(schema, dataset_id))
    except KeyError:
        pass
    try: 
        args['is_last']
        return("Success in sending data from Sesam into Power BI.")
    except KeyError:
        return ("Sending batch %i." % int(args['request_id']))


@app.route('/get_old_schemas', methods=['GET'])
def get_old_schemas(node_id, pipe_name):
    response = requests.get("https://%s.sesam.cloud/api/datasets/%s/entities" % (node_id, pipe_name), headers = Sesam_headers)
    if response.status_code == 200:
        logger.debug("Sent get request for pipe entities to Sesam node %s, pipe %s" % (node_id, pipe_name))
        return (response.json())
    else:
        logger.warning("Failed to get pipe entities from Sesam node %s, pipe %s" % (node_id, pipe_name))
        logger.warning("Url = https://%s.sesam.cloud/api/pipes" % node_id)
        logger.warning("response = %s" % str(response.status_code))


@app.route('/get_new_schema', methods=['GET'])
def get_new_schema(node_id, pipe_name):
    response = requests.get("https://%s.sesam.cloud/api/pipes/%s/generate-schema-definition" %(node_id, pipe_name), headers = Sesam_headers)
    if response.status_code == 200:
        logger.debug("Sent get request for schema to node id %s, pipe %s in Sesam" %(node_id, pipe_name))
        return response.json()
    else:
        logger.warning("Failed to send get schema from node id %s, pipe %s in Sesam" %(node_id, pipe_name))
        logger.warning("Url = https://%s.sesam.cloud/api/pipes/%s/generate-schema-definition" %(node_id, pipe_name))
        logger.warning("response = %s" % str(response.status_code))


@app.route('/update_schemas', methods=['POST'])
def update_schemas(node_id, pipe_name, schemas, new_schema):
    logger.info(schemas)
    if len(schemas) == 0:
        schemas.append(new_schema)
    else:
        for i, schema in enumerate(schemas):
            if schema["_id"] == new_schema["_id"]:
                schemas[i] = new_schema
    headers   = {'Authorization': "Bearer {}".format(get_env('SESAM-JWT')),"content_type": "application/json"}
    response = requests.post("https://%s.sesam.cloud/api/receivers/%s/entities" % (node_id, pipe_name), headers=headers, data=json.dumps(schemas))
    if response.status_code == 200:
        logger.debug("Posted Sesam schemas into dataset %s in Sesam node %s" %(pipe_name,node_id))
        return (response.json())
    else:
        logger.warning("Failed to post Sesam schema into dataset %s in Sesam node %s" %(pipe_name, node_id))
        logger.warning("Url = https://%s.sesam.cloud/api/receivers/%s/entities" % (node_id, pipe_name))
        logger.warning("response = %s" % str(response.status_code))


@app.route('/update_powerbi_columns', methods=['PUT'])
def update_powerbi_columns(dataset_id, dataset_name, table_name, data):
    response = requests.put(powerbi_url + "/%s/tables/%s" % (dataset_id, table_name), headers=Powerbi_headers, json=data)
    if response.status_code == 200:
        logger.debug("Updated the excisting columns in workspace %s, dataset %s, table %s in Power BI" %(workspace_id, dataset_name, table_name))
    else:
        logger.warning("Failed to update the excisting columns in workspace %s, dataset %s, table %s in Power BI" %(workspace_id, dataset_name, table_name))
        logger.warning("Url = %s/%s/tables/%s" % (powerbi_url, dataset_id, table_name))
        logger.warning("response = %s" % str(response.status_code))

@app.route('/delete_powerbi_rows', methods=['DELETE'])
def delete_powerbi_rows(dataset_id, dataset_name, table_name):
    response = requests.delete(powerbi_url + "/%s/tables/%s/rows" % (dataset_id, table_name), headers=Powerbi_headers)
    if response.status_code == 200:
        logger.debug("Deleted the excisting rows in workspace %s, dataset %s, table %s in Power BI" %(workspace_id, dataset_name, table_name))
    else:
        logger.warning("Failed to deleted the excisting rows in workspace %s, dataset %s, table %s in Power BI" %(workspace_id, dataset_name, table_name))
        logger.warning("Url = %s/%s/tables/%s" % (powerbi_url, dataset_id, table_name))
        logger.warning("response = %s" % str(response.status_code))


@app.route('/post_powerbi_rows', methods=['POST'])
def post_powerbi_rows(dataset_id, dataset_name, table_name, data):
    #table_name = "new_table"
    response = requests.post(powerbi_url + "/%s/tables/%s/rows" % (dataset_id, table_name), headers=Powerbi_headers, json=data)
    if response.status_code == 200:
        logger.debug("Posted rows into workspace %s, dataset %s, table %s in Power BI" %(workspace_id, dataset_name, table_name))
    else:
        logger.warning("Failed to post rows into workspace %s, dataset %s, table %s in Power BI" %(workspace_id, dataset_name, table_name))
        logger.warning("Url = %s/%s/tables/%s" % (powerbi_url, dataset_id, table_name))
        logger.warning("response = %s" % str(response.status_code))

@app.route('/create_powerbi_dataset', methods=['PUT'])
def create_powerbi_dataset(data, dataset_name, table_name):
    response = requests.post(powerbi_url,  headers=Powerbi_headers, json=data)

    if response.status_code == 201:
        logger.debug("Created dataset %s, table %s in workspace %s in Power BI" %(dataset_name, table_name, workspace_id))
    else:
        logger.warning("Failed to create dataset into dataset %s, table %s in workspace %s in Power BI" %(dataset_name, table_name, workspace_id))
        logger.warning("Url = %s" % powerbi_url)
        logger.warning("response = %s" % str(response.status_code))

@app.route('/get_powerbi', methods=['GET'])
def get_powerbi(dataset_id = str()):
    response    = requests.get(powerbi_url + dataset_id, headers=Powerbi_headers)
    if response.status_code == 200:
        logger.debug("Sent get request to workspace %s, dataset id %s in Power BI" %(workspace_id, dataset_id))
    else:
        logger.warning("Failed to send get request to workspace %s, dataset id %s in Power BI" %(workspace_id, dataset_id))
        logger.warning("Url = %s/%s" % (powerbi_url, dataset_id))
        logger.warning("response = %s" % str(response.status_code))
    return response

if __name__ == '__main__':

    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)