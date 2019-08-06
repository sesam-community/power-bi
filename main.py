from flask import Flask, request, jsonify
import json
from authentification.create_jwt import get_token
from authentification.auth_helpers import *
from processing.powerBi import *

app = Flask(__name__)
powerbi_url = "https://api.powerbi.com/v1.0/myorg/groups/07852248-6e81-49b3-b0ac-8c9e9d8c881f/datasets"
sesam_url   = "https://%s.sesam.cloud/api/pipes/%s" %(start_endpoint, pipe_name)

token           = get_token(client_id, tenant_id,refresh_token)
Powerbi_headers = {'Authorization': "Bearer {}".format(token['accessToken'])}
Sesam_headers     = {'Authorization': "Bearer {}".format(sesam_jwt)}

@app.route('/')
def index():
    output = {
        'service': 'Power BI Connector',
        'remote_addr': request.remote_addr
    }
    return jsonify(output)


@app.route('/get_powerbi', methods=['GET'])
def get_powerbi(dataset_id = str()):
    response    = requests.get(powerbi_url + dataset_id, headers=Powerbi_headers)
    return response

@app.route('/get_sesam', methods=['GET'])
def get_sesam(entities = str()):
    response    = requests.get(sesam_url + entities, headers=Sesam_headers)
    return response

@app.route('/delete_powerbi', methods=['DELETE'])
def delete_powerbi(dataset_id, table_name):
    requests.delete(powerbi_url + '/' + dataset_id + '/tables/%s/rows' %table_name, headers=Powerbi_headers)

@app.route('/post_data', methods=['GET', 'POST'])
def posting_data():

    # Fetching the Sesam data
    Sesam_data      = get_sesam().json()
    entities        = get_sesam('/entities').json()

    # Setting up the Power BI table in the correct format
    table           = setup_table(Sesam_data['_id'])
     
    # Populating the columns (properties)
    populated_table = add_columns(table, entities)

    # If the dataset from Sesam already exists in Power BI, 
    # the Power BI dataset gets deleted and replaced by the new one
    
    current_datasets            = get_powerbi()
    dataset_exists, dataset_id  = check_dataset(current_datasets.json(), populated_table['name'])
    if dataset_exists:
      delete_powerbi(dataset_id, populated_table['name'])
    
    #response        = requests.post(powerbi_url, headers=Powerbi_headers, json=populated_table)
    #dataset_id      = response.json()['id']
    
    #Populating the rows (entities)
    rows            = add_rows(entities)
    # Adding rows to table in Power BI
    requests.post(powerbi_url + "/%s/tables/%s/rows" % (dataset_id, populated_table['name']), headers=Powerbi_headers, json=rows)

    response        = get_powerbi('/' + dataset_id)
    return jsonify(response.json())


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)
