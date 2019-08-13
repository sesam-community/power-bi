from flask import Flask, request, jsonify
import json
from authentification.create_jwt import get_token
#from authentification.auth_helpers import *
from processing.powerBi import *
#from authentification.set_config import *
import sys
import os
import time


app           = Flask(__name__)
print(11)
#sesam_jwt = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE1NjU1OTM4MjIuOTg3MzA0NywiZXhwIjoxNTk3MjE2MDg5LCJ1c2VyX2lkIjoiNDI1YzQ3YTctNWE4Yi00ZjY1LWEyYzQtMTljNzNiZmRmNGQ3IiwidXNlcl9wcm9maWxlIjp7ImVtYWlsIjoiZXJpay5sZXZlbkBzZXNhbS5pbyIsIm5hbWUiOiJlcmlrLmxldmVuQHNlc2FtLmlvIiwicGljdHVyZSI6Imh0dHBzOi8vcy5ncmF2YXRhci5jb20vYXZhdGFyLzZjYmQxYjkyNTQwNWMyOTVkN2ZmYWQ5M2Y2ODRlODQ2P3M9NDgwJnI9cGcmZD1odHRwcyUzQSUyRiUyRmNkbi5hdXRoMC5jb20lMkZhdmF0YXJzJTJGZWEucG5nIn0sInVzZXJfcHJpbmNpcGFsIjoiZ3JvdXA6RXZlcnlvbmUiLCJwcmluY2lwYWxzIjp7IjBiMDhiNTBiLTZkNDAtNGI4MC1iZDI4LWMzMDM2NjA2NWRhNSI6WyJncm91cDpBZG1pbiJdfSwiYXBpX3Rva2VuX2lkIjoiZDQxMjRmNmMtZTU0OS00MDFiLWJjZjAtNTQxZTM1MGVlMjgyIn0.F5gS8jtzKg-EYdca5nHojy79jC8q-hd4FnUEu2oSUBAu5mDMLiV9ohBvZmWmAwnjy3ABWn3oO-vvd8J46xp4I-SoQHmdb06ttTxHhKq0XzZiXiNsnj59u3IJJTWzUdpEnyUd0Y_fVYjMDDczEY86Lwo8t4Stmp1voZzHxOzE4w690KNZ_l2PlHKtpKRVTqCjfyhGuQwzn2SXBqE4ZKz2DCDqBmPq6Mjiybt-r5Z3m-NUesecZwEBO8_lGXlc3wEHACCFIbiN9zKIxYVdXS0TW7_exADWMNrBQEc3oz11f-y3oSR1SpceC2mwbCh7r5ln2jvghGgFTbM53x5TBLmE5Q"
#pbi_client_id = "31cb468e-3d61-4246-851f-e8162f8e0a44"
#tenant_id = "7bcbcc45-fb12-41d3-8ace-fa0fffaebf1d"
#pbi_refresh_token = "AQABAAAAAAAP0wLlqdLVToOpA4kwzSnxzzCXODGOf6W2Aw0m-cbXcDypYHRnMI5i6SMsHEwp2mxWSr1yadncwqotASRV2evNBT62sklJ_uRIOrt8fKqLso-ykm64Q3YPWLtMVmVSQG5BVqTKPX5PnI7p4YcOB-VB6weKHmYrZnVwbVgV9GK9EaLMIGZZ_vTvOUMG5DX_EIEtKxtkfbJG4kIZstty7ue3a_xk90uVPtF7v3yUVL8QZK2Vm__YC-XvH5lV3LuD3D3OS20VYxl7xcGMVTUVvbrLWQJustOJ7S9jjp-bxy5hq1W0WHVrhkkkG-EZdhyrjBy_onWm1oG1IQVBYKq54Cs-bYmQubZvdMQ_0EIUih4xkWcjqXx7fRDIPoGy5599npQCGAuVF3RtNcGiVdnD1-5j6_DlqreYTibRkkYMjjCbdPVdKFwoZc7xmlLSxw2m1uj6jA_MqutD_y9-AvKMgpgToWxM3SPZQbrwvG7XCdj-DPxjqL_rOaC-4Dp1Z4Mvb5YGlBA8pOaD9hm4waf6yaTDiPsmFvtWJ4ztpSZDB6USY14cPbe0N2w2yCJBaCoJfDCfJd3C9yOfvT8FVFHNyRijfYnTWAjjUMemJYDnOUefLUqzqIaZilS6XYjp5yER8KK-OlBMDiebU9FAOi1EzfKU_YxLRQvd4KUZI4Kkx8VqBnA-lBwviD2OKZ3Dkk8bz48O26Wre7zcMbTLkYxGou0Hn6JdOGi4neYJOX8MXU_s3ijdUpr_CWa4eJx-6N7n_awlnS5clpAS821I9o3EfJDC-oDQ0z9NAM5dPbFbAewaM6735erOP3eGJsaosfRhjrp8eus7ysCHUKlwDcsMUOFdfGDX8btmFlK2zS-gqxrGDu-kbu7rh9tlnWLvcDEePan0tNYpcGHVjngFtd2uXqQmIAA"
#token           = get_token(pbi_client_id, tenant_id,pbi_refresh_token)
    
#Powerbi_headers = {'Authorization': "Bearer {}".format(token['accessToken'])}
#Sesam_headers   = {'Authorization': "Bearer {}".format(sesam_jwt)}
#workspace_id = "07852248-6e81-49b3-b0ac-8c9e9d8c881f"
#powerbi_url       = "https://api.powerbi.com/v1.0/myorg/groups/%s/datasets" % workspace_id

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


@app.route('/get_sesam/<node_id>/<pipe_name>', methods=['POST'])
def pipe(node_id, pipe_name):

    entities = request.get_json()#"https://%s.sesam.cloud/api/pipes/%s/entities" %(node_id, pipe_name), headers=Sesam_headers)
    print(2)
    schema   = requests.get("https://%s.sesam.cloud/api/pipes/%s/generate-schema-definition" %(node_id, pipe_name), headers = Sesam_headers).json()
    dataset                 = setup_dataset(pipe_name)
    print(3)
    populated_dataset, keys = add_columns(dataset, entities, schema)
    rows                    = add_rows(entities, populated_dataset, keys)

    # If the dataset from Sesam already exists in Power BI, the Power BI dataset gets updated
    current_datasets                        = get_powerbi(workspace_id)
    print(4)
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
    #requests.post(powerbi_url + "/%s/tables/%s/rows" % (dataset_id, pipe_name), headers=Powerbi_headers, json=rows)
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
