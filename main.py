from flask import Flask, request, jsonify
import json
from authentification.create_jwt import get_token
from authentification.auth_helpers import *
from processing.powerBi import *
import sys

app           = Flask(__name__)
powerbi_url   = "https://api.powerbi.com/v1.0/myorg/groups/07852248-6e81-49b3-b0ac-8c9e9d8c881f/datasets"
sesam_url     = "https://%s.sesam.cloud/api/pipes/%s" %(start_endpoint, pipe_name)

token           = get_token(client_id, tenant_id,refresh_token)
Powerbi_headers = {'Authorization': "Bearer {}".format(token['accessToken'])}
Sesam_headers   = {'Authorization': "Bearer {}".format(sesam_jwt)}



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
    
def delete_all_datasets(response):
  response = get_powerbi()
  for data in response.json()['value']:
    delete_powerbi(data['id'])


@app.route('/post_data', methods=['GET', 'POST'])
def posting_data():
    update_rows    = False
    update_columns = False
    new_dataset    = False

    # Fetching the Sesam data
    #schema = [{'type': 'string', 'max_size': 9, 'min_size': 0, 'source_property': 'power-bi-embedded:global-company:company-id', 'name': 'power-bi-embedded:global-company:company-id'}, {'type': 'string', 'max_size': 10, 'min_size': 0, 'source_property': 'power-bi-embedded:global-company:name', 'name': 'power-bi-embedded:global-company:name', 'allow_null': True}, {'type': 'string', 'max_size': 8, 'min_size': 0, 'source_property': 'power-bi-embedded:global-company:phone', 'name': 'power-bi-embedded:global-company:phone'}, {'type': 'decimal', 'precision': 4, 'scale': 3, 'max_value': '~f9.812', 'min_value': '~f9.812', 'source_property': 'power-bi-embedded:global-invoice-detail:currency-value', 'name': 'power-bi-embedded:global-invoice-detail:currency-value'}, {'type': 'boolean', 'source_property': 'power-bi-embedded:global-invoice-detail:internal', 'name': 'power-bi-embedded:global-invoice-detail:internal', 'allow_null': True}, {'type': 'boolean', 'source_property': 'power-bi-embedded:global-invoice-detail:invoice', 'name': 'power-bi-embedded:global-invoice-detail:invoice'}, {'type': 'datetime', 'max_value': '~t2019-08-01T00:00:00Z', 'min_value': '~t2019-08-01T00:00:00Z', 'source_property': 'power-bi-embedded:global-invoice-detail:invoice-date', 'name': 'power-bi-embedded:global-invoice-detail:invoice-date'}, {'type': 'string', 'max_size': 58, 'min_size': 0, 'index': True, 'source_property': 'power-bi-embedded:global-invoice-detail:invoice-ni', 'name': 'power-bi-embedded:global-invoice-detail:invoice-ni'}, {'type': 'boolean', 'source_property': 'power-bi-embedded:global-invoice-detail:invoiced', 'name': 'power-bi-embedded:global-invoice-detail:invoiced'}, {'type': 'decimal', 'precision': 4, 'scale': 1, 'max_value': '~f300.0', 'min_value': '~f300.0', 'source_property': 'power-bi-embedded:global-invoice-detail:max', 'name': 'power-bi-embedded:global-invoice-detail:max'}, {'type': 'string', 'max_size': 21, 'min_size': 0, 'source_property': 'power-bi-embedded:global-invoice-detail:name', 'name': 'power-bi-embedded:global-invoice-detail:name'}, {'type': 'string', 'max_size': 20, 'min_size': 0, 'index': True, 'source_property': 'power-bi-embedded:global-invoice-detail:period-ni', 'name': 'power-bi-embedded:global-invoice-detail:period-ni'}, {'type': 'string', 'max_size': 24, 'min_size': 0, 'index': True, 'source_property': 'power-bi-embedded:global-invoice-detail:product-ni', 'name': 'power-bi-embedded:global-invoice-detail:product-ni'}, {'type': 'decimal', 'precision': 3, 'scale': 1, 'max_value': '~f31.0', 'min_value': '~f31.0', 'source_property': 'power-bi-embedded:global-invoice-detail:quantity', 'name': 'power-bi-embedded:global-invoice-detail:quantity'}, {'type': 'decimal', 'precision': 9, 'scale': 5, 'max_value': '~f4562.58000', 'min_value': '~f4562.58000', 'source_property': 'power-bi-embedded:global-invoice-detail:total-price', 'name': 'power-bi-embedded:global-invoice-detail:total-price'}, {'type': 'string', 'max_size': 12, 'min_size': 0, 'source_property': 'power-bi-embedded:global-invoice-detail:unit', 'name': 'power-bi-embedded:global-invoice-detail:unit', 'allow_null': True}, {'type': 'decimal', 'precision': 3, 'scale': 1, 'max_value': '~f15.0', 'min_value': '~f15.0', 'source_property': 'power-bi-embedded:global-invoice-detail:unit-price', 'name': 'power-bi-embedded:global-invoice-detail:unit-price'}, {'type': 'boolean', 'source_property': 'power-bi-embedded:global-paymentmethod:billable', 'name': 'power-bi-embedded:global-paymentmethod:billable', 'allow_null': True}, {'type': 'string', 'max_size': 26, 'min_size': 0, 'index': True, 'source_property': 'power-bi-embedded:global-paymentmethod:company-ni', 'name': 'power-bi-embedded:global-paymentmethod:company-ni'}, {'type': 'string', 'max_size': 3, 'min_size': 0, 'source_property': 'power-bi-embedded:global-paymentmethod:currency', 'name': 'power-bi-embedded:global-paymentmethod:currency'}, {'type': 'boolean', 'source_property': 'power-bi-embedded:global-paymentmethod:internal', 'name': 'power-bi-embedded:global-paymentmethod:internal'}, {'type': 'string', 'max_size': 24, 'min_size': 0, 'source_property': 'power-bi-embedded:global-paymentmethod:name', 'name': 'power-bi-embedded:global-paymentmethod:name'}, {'type': 'datetime', 'max_value': '~t2019-08-31T23:59:59Z', 'min_value': '~t2019-08-31T23:59:59Z', 'source_property': 'power-bi-embedded:global-period:end', 'name': 'power-bi-embedded:global-period:end'}, {'type': 'string', 'max_size': 10, 'min_size': 0, 'source_property': 'power-bi-embedded:global-period:resource-date', 'name': 'power-bi-embedded:global-period:resource-date', 'allow_null': True}, {'type': 'decimal', 'precision': 4, 'scale': 1, 'max_value': '~f300.0', 'min_value': '~f300.0', 'source_property': 'power-bi-embedded:global-product:rate', 'name': 'power-bi-embedded:global-product:rate'}]
    
    #response = get_sesam("/entities")#?since=1&limit=8")
    response = get_sesam("/entities?since=1&limit=8")
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
    dataset           = setup_dataset(pipe_name)
    populated_dataset, keys = add_columns(dataset, entities, schema)
    rows            = add_rows(entities, populated_dataset, keys)

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
