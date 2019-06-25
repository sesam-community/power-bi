import requests

def get_sesam_data(jwt):
    start_endpoint = 'datahub-3dab4200'
    url = 'https://' + start_endpoint + '.sesam.cloud/api/pipes/automagic-mysql-VBJMMMDQ-user-agent'
    ##print(url)
    header = {'Authorization': "Bearer {}".format(jwt)}
    response = requests.get(url,headers=header)
    return response