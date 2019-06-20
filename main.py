from flask import Flask, request, jsonify
import json
import requests

app = Flask(__name__)

@app.route('/')
def index():
    output = {
        'service': 'Power BI Connector',
        'remote_addr': request.remote_addr
    }
    return jsonify(output)

@app.route('/get_data', methods=['GET'])
def getting_powerbidata():
    response = requests.get("https://api.powerbi.com/v1.0/myorg/datasets/cfafbeb1-8037-4d0c-896e-a46fb27ff229")
    print(response)
    return jsonify({"Response": "You just got swaggered!"})

if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)