from flask import Flask, request, jsonify
import json
from authentification.create_jwt import get_token
from authentification.auth_helpers import *
from processing.powerBi import *
from authentification.set_config import *
import sys

app           = Flask(__name__)

if len(sys.argv) != 2:
    print('Need the path to the config file as command-line argument')
    print('exiting..')
    sys.exit()

config_file = sys.argv[1]
mappings = set_environ(config_file)

def get_env(var):
    envvar = None
    if var.upper() in os.environ:
        envvar = os.environ[var.upper()]
    return envvar


token           = get_token(get_env('pbi_client_id'), get_env('tenant_id'),get_env('pbi_refresh_token'))
Powerbi_headers = {'Authorization': "Bearer {}".format(token['accessToken'])}
Sesam_headers   = {'Authorization': "Bearer {}".format(get_env('sesam_jwt'))}



def delete_all_datasets(response):
  response = get_powerbi()
  for data in response.json()['value']:
    delete_powerbi(data['id'])

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
def get_sesam(endpoint = str()):
    response    = requests.get(sesam_url + endpoint, headers=Sesam_headers)
    return response

@app.route('/update_powerbi_rows', methods=['DELETE'])
def delete_powerbi_rows(dataset_id, table_name):
    requests.delete(powerbi_url + '/' + dataset_id + '/tables/%s/rows' %table_name, headers=Powerbi_headers)

@app.route('/update_powerbi_columns', methods=['DELETE'])
def delete_powerbi_columns(dataset_id):
    requests.delete(powerbi_url + '/' + dataset_id, headers=Powerbi_headers)
    
@app.route('/post_data', methods=['GET', 'POST'])
def posting_data():

    update_rows    = False
    update_columns = False
    new_dataset    = False

    # Fetching the Sesam data
    #response = get_sesam("/entities")#?since=1&limit=8")
    #print("/entities?since=%s&limit=%s" %(mappings[0]['sesam_since'], mappings[0]['sesam_limit']))
    #ss
    response = get_sesam("/entities?since=%s&limit=%s"%(mappings[0]['sesam_since'], mappings[0]['sesam_limit']))

    if response.status_code != 200:
        print(response)
        print('bad request fo Sesam')
        sys.exit()
    else:
        entities = response.json()

    schema = [{'type': 'string', 'max_size': 23, 'min_size': 8, 'allow_null': True, 'source_property': 'global-company:name', 'name': 'global-company:name'}, {'type': 'decimal', 'precision': 5, 'scale': 4, 'max_value': '~f9.9483', 'min_value': '~f9.4125', 'source_property': 'global-invoice-detail:currency-value', 'name': 'global-invoice-detail:currency-value'}, {'type': 'datetime', 'max_value': '~t2019-04-01T00:00:00Z', 'min_value': '~t2017-10-01T00:00:00Z', 'source_property': 'global-invoice-detail:invoice-date', 'name': 'global-invoice-detail:invoice-date'}, {'type': 'decimal', 'precision': 12, 'scale': 6, 'max_value': '~f102899.161600', 'min_value': '~f0.00000', 'source_property': 'global-invoice-detail:total-price', 'name': 'global-invoice-detail:total-price'}, {'type': 'decimal', 'precision': 5, 'scale': 1, 'max_value': '~f1500.0', 'min_value': '~f0.0', 'source_property': 'global-invoice-detail:unit-price', 'name': 'global-invoice-detail:unit-price'}, {'type': 'boolean', 'allow_null': True, 'source_property': 'global-paymentmethod:billable', 'name': 'global-paymentmethod:billable'}]
    #ss
    #schema          = get_sesam("/generate-schema-definition").json()
    #print(schema)
    #ss

    # Setting up the Power BI table in the correct format
    dataset                 = setup_dataset(pipe_name)
    populated_dataset, keys = add_columns(dataset, entities, schema)
    rows                    = add_rows(entities, populated_dataset, keys)

    # If the dataset from Sesam already exists in Power BI, 
    # the Power BI dataset gets updated
    
    current_datasets            = get_powerbi()
    update_rows, update_columns, new_dataset, dataset_id = check_dataset_status(current_datasets, entities, pipe_name, update_rows, update_columns, new_dataset)
    if not update_rows:
      if update_columns:
        delete_powerbi_columns(dataset_id)
        requests.post(powerbi_url, headers=Powerbi_headers, json=populated_dataset)
      else:
        requests.post(powerbi_url, headers=Powerbi_headers, json=populated_dataset)
      response = get_powerbi()
      dataset_id = find_dataset_id(response, pipe_name)
    else:
      delete_powerbi_rows(dataset_id, pipe_name)

    # Populating the rows in the dataset
    requests.post(powerbi_url + "/%s/tables/%s/rows" % (dataset_id, pipe_name), headers=Powerbi_headers, json=rows)
    response        = get_powerbi('/' + dataset_id)
    
    return jsonify(response.json())


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)
