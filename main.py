from flask import Flask, request, jsonify
import json
from authentification.create_jwt import get_token
from authentification.auth_helpers import *
from sesam.getting_sesam_data import get_sesam_data
from processing.powerBi import *

app = Flask(__name__)
url_dataset = "https://api.powerbi.com/v1.0/myorg/datasets"


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
    response = requests.get("https://api.powerbi.com/v1.0/myorg/datasets", headers=headers)
    Sesam_data  = get_sesam_data(sesam_jwt, start_endpoint, pipe_name).json()
    return jsonify(Sesam_data)

@app.route('/post_data', methods=['GET','POST','DELETE'])
def posting_data():

    token       = get_token(client_id, tenant_id,refresh_token)
    headers     = {'Authorization': "Bearer {}".format(token['accessToken'])}
    
    Sesam_data  = get_sesam_data(sesam_jwt, start_endpoint, pipe_name).json()
    new_table_name = Sesam_data['_id']
    table       = setup_table(Sesam_data)
    Sesam_data  = strip_Sesam_data(Sesam_data)
      
    current_datasets  = requests.get(url_dataset, headers=headers)    
    populated_table   = add_columns(table, Sesam_data, headers)
    dataset_exists, dataset_id = check_dataset(current_datasets.json(), populated_table['name'])

    # If a dataset already exists, it gets deleted and replaced by the new one
    if dataset_exists:
      requests.delete(url_dataset + "/" + dataset_id, headers=headers)
    requests.post(url_dataset, headers=headers, json=populated_table)

    response = requests.get(url_dataset, headers=headers)
    dataset_exists, dataset_id = check_dataset(response.json(), populated_table['name'])

    #Populating the rows (entities)
    rows = add_rows(Sesam_data)
    
    response = requests.post(url_dataset + "/%s/tables/%s/rows" % (dataset_id, new_table_name), headers=headers, json=rows)
    response = requests.get(url_dataset + "/%s/tables" % dataset_id, headers=headers)

    return jsonify(response.json())


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)
