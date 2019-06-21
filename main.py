from flask import Flask, request, jsonify
import json
import requests

app = Flask(__name__)

## testing
## Setting helpers
AppID = "8df57daa-57e6-4044-9d3f-33aee3171de8"
AppSecret = "AXov1dtKsZjakaxr0oh3zUiyVsRD3vwfBBgKwTSc3dE"
##

@app.route('/')
def index():
    output = {
        'service': 'Power BI Connector',
        'remote_addr': request.remote_addr
    }
    return jsonify(output)

@app.route('/get_data', methods=['GET'])
def getting_data():
    response = requests.get("https://api.powerbi.com/v1.0/myorg/datasets/%s" % AppID)
    print(response)
    return jsonify({"Response": "You just got swaggered!"})

@app.route('/post_data', methods=['GET','POST'])
def posting_data():
    output = {
        'Erik': 'Does something magical!'
    }
    return jsonify(output)

if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)