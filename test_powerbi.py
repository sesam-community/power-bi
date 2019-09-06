import requests
from flask import Flask, request, jsonify
import json
import os
import logging


app           = Flask(__name__)

def get_env(var):
    envvar = None
    if var.upper() in os.environ:
        envvar = os.environ[var.upper()]
    return envvar

def make_entities(num_entities, num_properties):
    entities = []
    for i in range(num_entities):
        entities.append({})
        entities[i]['_id'] = str(i+1)
        for j in range(num_properties):
            entities[i]["property_%i"%j] = str(i*10 + j + 1)
    return entities

@app.route('/', methods=['GET'])
def index():
    kk = True
    print("hh") if kk else 0
    app.logger.debug("hey") if kk else 0
    return ("index")

@app.route('/post/<node_id>/<dataset_name>/<num_entities>/<num_properties>', methods=['GET'])
def post(node_id, pipe_name, num_entities, num_properties):
    Sesam_headers   = {'Authorization': "Bearer {}".format(get_env('JWT')), "content_type": "application/json"}
    foo=requests.post("https://%s.sesam.cloud/api/receivers/%s/entities" %(node_id, dataset_name), headers=Sesam_headers, data=json.dumps(make_entities(num_entities,num_properties)))
    return ("Status code %i" %foo.status_code)


if __name__ == '__main__':

    logger = logging.getLogger('powerbi-test')
    format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    # Log to stdout
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(stdout_handler)

    logger.setLevel(logging.DEBUG)

    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
