import requests

def get_sesam_data(jwt, datahub_url):
    url = 'https://' + datahub_url + '.sesam.cloud/api/pipes/crm-person'
    header = {'Authorization': "Bearer {}".format(jwt)}
    response = requests.get(url,headers=header)
    return response