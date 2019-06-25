import requests

def get_sesam_data(jwt, start_endpoint):
    url = 'https://' + start_endpoint + '.sesam.cloud/api/pipes/crm-person'
    ##print(url)
    header = {'Authorization': "Bearer {}".format(jwt)}
    response = requests.get(url,headers=header)
    return response