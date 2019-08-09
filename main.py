from flask import Flask, request, jsonify
import json
from authentification.create_jwt import get_token
from authentification.auth_helpers import *
from processing.powerBi import *
from authentification.set_config import *
import sys


app           = Flask(__name__)

def get_env(var):
    envvar = None
    if var.upper() in os.environ:
        envvar = os.environ[var.upper()]
    return envvar

def check_request_status(response):
    if response.status_code != 200:
        print(response)
        print('Bad request fo Sesam')
        sys.exit()
    else:
        return response.json()

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
    # Fetching the Sesam data
    response = get_sesam("%s/entities?since=%s&limit=%s"%(pipe_name, sesam_since, sesam_limit))
    entities = check_request_status(response)
    #schema   = get_sesam("%s/generate-schema-definition" % pipe_name).json()

    schema   = [{'type': 'string', 'max_size': 9, 'min_size': 9, 'source_property': 'global-company:company-id', 'name': 'global-company:company-id', 'allow_null': True}, {'type': 'string', 'max_size': 23, 'min_size': 8, 'source_property': 'global-company:name', 'name': 'global-company:name', 'allow_null': True}, {'type': 'string', 'max_size': 11, 'min_size': 5, 'source_property': 'global-company:phone', 'name': 'global-company:phone', 'allow_null': True}, {'type': 'string', 'max_size': 22, 'min_size': 11, 'source_property': 'global-company:url', 'name': 'global-company:url', 'allow_null': True}, {'type': 'string', 'max_size': 3, 'min_size': 3, 'source_property': 'global-invoice-detail:currency-base', 'name': 'global-invoice-detail:currency-base'}, {'type': 'string', 'max_size': 33, 'min_size': 33, 'index': True, 'source_property': 'global-invoice-detail:currency-ni', 'name': 'global-invoice-detail:currency-ni', 'allow_null': True}, {'type': 'string', 'max_size': 3, 'min_size': 3, 'source_property': 'global-invoice-detail:currency-target', 'name': 'global-invoice-detail:currency-target'}, {'type': 'decimal', 'precision': 5, 'scale': 4, 'max_value': '~f9.9483', 'min_value': '~f9.4125', 'source_property': 'global-invoice-detail:currency-value', 'name': 'global-invoice-detail:currency-value'}, {'type': 'string', 'max_size': 85, 'min_size': 68, 'index': True, 'source_property': 'global-invoice-detail:invoice-basis-ni', 'name': 'global-invoice-detail:invoice-basis-ni', 'allow_null': True}, {'type': 'datetime', 'max_value': '~t2019-04-01T00:00:00Z', 'min_value': '~t2017-10-01T00:00:00Z', 'source_property': 'global-invoice-detail:invoice-date', 'name': 'global-invoice-detail:invoice-date'}, {'type': 'string', 'max_size': 0, 'min_size': 0, 'source_property': 'global-invoice-detail:invoice-id', 'name': 'global-invoice-detail:invoice-id'}, {'type': 'string', 'max_size': 58, 'min_size': 54, 'index': True, 'source_property': 'global-invoice-detail:invoice-ni', 'name': 'global-invoice-detail:invoice-ni'}, {'type': 'boolean', 'source_property': 'global-invoice-detail:invoiced', 'name': 'global-invoice-detail:invoiced'}, {'type': 'string', 'max_size': 44, 'min_size': 3, 'source_property': 'global-invoice-detail:name', 'name': 'global-invoice-detail:name'}, {'type': 'string', 'max_size': 62, 'min_size': 58, 'index': True, 'source_property': 'global-invoice-detail:paymentmethod-ni', 'name': 'global-invoice-detail:paymentmethod-ni'}, {'type': 'string', 'max_size': 20, 'min_size': 20, 'index': True, 'source_property': 'global-invoice-detail:period-ni', 'name': 'global-invoice-detail:period-ni'}, {'type': 'string', 'max_size': 26, 'min_size': 17, 'index': True, 'source_property': 'global-invoice-detail:product-ni', 'name': 'global-invoice-detail:product-ni'}, {'type': 'string', 'max_size': 71, 'min_size': 27, 'source_property': 'global-invoice-detail:product-title', 'name': 'global-invoice-detail:product-title'}, {'type': 'decimal', 'precision': 5, 'scale': 1, 'max_value': '~f1059.2', 'min_value': '~f0.0', 'source_property': 'global-invoice-detail:quantity', 'name': 'global-invoice-detail:quantity'}, {'type': 'boolean', 'source_property': 'global-invoice-detail:ready', 'name': 'global-invoice-detail:ready', 'allow_null': True}, {'type': 'string', 'max_size': 68, 'min_size': 68, 'index': True, 'source_property': 'global-invoice-detail:subscription-ni', 'name': 'global-invoice-detail:subscription-ni', 'allow_null': True}, {'type': 'decimal', 'precision': 12, 'scale': 6, 'max_value': '~f102899.161600', 'min_value': '~f0.00000', 'source_property': 'global-invoice-detail:total-price', 'name': 'global-invoice-detail:total-price'}, {'type': 'string', 'max_size': 15, 'min_size': 12, 'source_property': 'global-invoice-detail:unit', 'name': 'global-invoice-detail:unit'}, {'type': 'decimal', 'precision': 5, 'scale': 1, 'max_value': '~f1500.0', 'min_value': '~f0.0', 'source_property': 'global-invoice-detail:unit-price', 'name': 'global-invoice-detail:unit-price'}, {'type': 'boolean', 'source_property': 'global-paymentmethod:billable', 'name': 'global-paymentmethod:billable', 'allow_null': True}, {'type': 'string', 'max_size': 26, 'min_size': 26, 'index': True, 'source_property': 'global-paymentmethod:company-ni', 'name': 'global-paymentmethod:company-ni', 'allow_null': True}, {'type': 'string', 'max_size': 3, 'min_size': 3, 'source_property': 'global-paymentmethod:currency', 'name': 'global-paymentmethod:currency', 'allow_null': True}, {'type': 'boolean', 'source_property': 'global-paymentmethod:internal', 'name': 'global-paymentmethod:internal', 'allow_null': True}, {'type': 'string', 'max_size': 25, 'min_size': 4, 'source_property': 'global-paymentmethod:name', 'name': 'global-paymentmethod:name', 'allow_null': True}, {'type': 'string', 'max_size': 20, 'min_size': 20, 'index': True, 'source_property': 'global-paymentmethod:project-ni', 'name': 'global-paymentmethod:project-ni', 'allow_null': True}, {'type': 'datetime', 'max_value': '~t2019-04-30T23:59:59Z', 'min_value': '~t2017-10-31T23:59:59Z', 'source_property': 'global-period:end', 'name': 'global-period:end'}, {'type': 'string', 'max_size': 10, 'min_size': 10, 'source_property': 'global-period:resource-date', 'name': 'global-period:resource-date'}, {'type': 'datetime', 'max_value': '~t2019-04-01T00:00:00Z', 'min_value': '~t2017-10-01T00:00:00Z', 'source_property': 'global-period:start', 'name': 'global-period:start'}, {'type': 'string', 'max_size': 16, 'min_size': 4, 'source_property': 'global-product:category', 'name': 'global-product:category'}, {'type': 'datetime', 'max_value': '~t2019-04-01T00:00:00Z', 'min_value': '~t2017-10-01T00:00:00Z', 'source_property': 'timestamp', 'name': 'timestamp'}, {'type': 'null', 'warning': "Column type could not be inferred - 'integer' will be used as a fallback", 'allow_null': True, 'source_property': 'global-invoice-detail:project-ni', 'name': 'global-invoice-detail:project-ni'}, {'type': 'string', 'max_size': 39, 'min_size': 29, 'index': True, 'source_property': 'global-product:product-category-ni', 'name': 'global-product:product-category-ni', 'allow_null': True}, {'type': 'string', 'max_size': 25, 'min_size': 24, 'index': True, 'source_property': 'global-project:company-ni', 'name': 'global-project:company-ni', 'allow_null': True}, {'type': 'string', 'max_size': 44, 'min_size': 24, 'source_property': 'global-project:name', 'name': 'global-project:name', 'allow_null': True}, {'type': 'datetime', 'max_value': '~t2019-04-01T00:00:00Z', 'min_value': '~t2016-12-15T00:00:00Z', 'source_property': 'global-project:start', 'name': 'global-project:start', 'allow_null': True}, {'type': 'datetime', 'max_value': '~t2034-01-31T00:00:00Z', 'min_value': '~t2024-12-19T00:00:00Z', 'source_property': 'global-project:stop', 'name': 'global-project:stop', 'allow_null': True}, {'type': 'string', 'max_size': 3, 'min_size': 3, 'source_property': 'global-paymentmethod:fixed_currency', 'name': 'global-paymentmethod:fixed_currency', 'allow_null': True}, {'type': 'integer', 'max_value': 267803, 'min_value': 160, 'source_property': 'global-paymentmethod:fixed_price', 'name': 'global-paymentmethod:fixed_price', 'allow_null': True}, {'type': 'boolean', 'source_property': 'global-invoice-detail:internal', 'name': 'global-invoice-detail:internal', 'allow_null': True}, {'type': 'null', 'warning': "Column type could not be inferred - 'integer' will be used as a fallback", 'allow_null': True, 'source_property': 'global-invoice-detail:invoice', 'name': 'global-invoice-detail:invoice'}, {'type': 'string', 'max_size': 67, 'min_size': 67, 'source_property': 'global-product:name', 'name': 'global-product:name', 'allow_null': True}, {'type': 'string', 'max_size': 36, 'min_size': 36, 'source_property': 'invoice-internal-review:paymentmethod', 'name': 'invoice-internal-review:paymentmethod', 'allow_null': True}, {'type': 'null', 'warning': "Column type could not be inferred - 'integer' will be used as a fallback", 'allow_null': True, 'source_property': 'global-product:rate', 'name': 'global-product:rate'}, {'type': 'boolean', 'source_property': 'invoice-review-history:invoice', 'name': 'invoice-review-history:invoice', 'allow_null': True}, {'type': 'string', 'max_size': 20, 'min_size': 20, 'index': True, 'source_property': 'invoice-review-history:project-ni', 'name': 'invoice-review-history:project-ni', 'allow_null': True}, {'type': 'string', 'max_size': 36, 'min_size': 32, 'source_property': 'invoice-review:paymentmethod', 'name': 'invoice-review:paymentmethod', 'allow_null': True}]

    # Setting up the Power BI table in the correct format
    dataset                 = setup_dataset(pipe_name)
    populated_dataset, keys = add_columns(dataset, entities, schema)
    rows                    = add_rows(entities, populated_dataset, keys)

    # If the dataset from Sesam already exists in Power BI, the Power BI dataset gets updated
    current_datasets                        = get_powerbi()
    update_rows, update_columns, dataset_id = check_dataset_status(current_datasets, entities, pipe_name)

    if update_rows:
        delete_powerbi_rows(dataset_id, pipe_name)
    else:
        if update_columns:
            delete_powerbi_columns(dataset_id)
            requests.post(powerbi_url, headers=Powerbi_headers, json=populated_dataset)
        else: # if new_dataset
            requests.post(powerbi_url, headers=Powerbi_headers, json=populated_dataset)
        response    = get_powerbi()
        dataset_id  = find_dataset_id(response, pipe_name)

    # Populating the rows in the dataset
    requests.post(powerbi_url + "/%s/tables/%s/rows" % (dataset_id, pipe_name), headers=Powerbi_headers, json=rows)
    response        = get_powerbi('/' + dataset_id)
    return jsonify(response.json())


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Please insert the path to the config file as command-line argument')
        print('Exiting..')
        sys.exit()

    config_file     = sys.argv[1]
    mappings        = set_environ(config_file)
    pipe_name       = mappings[0]['target_dataset_id']
    sesam_since     = mappings[0]['sesam_since']
    sesam_limit     = mappings[0]['sesam_limit']
    token           = get_token(get_env('pbi_client_id'), get_env('tenant_id'),get_env('pbi_refresh_token'))
    Powerbi_headers = {'Authorization': "Bearer {}".format(token['accessToken'])}
    Sesam_headers   = {'Authorization': "Bearer {}".format(get_env('sesam_jwt'))}

    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)
