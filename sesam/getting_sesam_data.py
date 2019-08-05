import requests

def get_sesam_data(jwt, start_endpoint, pipe_name):
    url 	 = 'https://' + start_endpoint + '.sesam.cloud/api/pipes/%s/entities' %pipe_name
    header   = {'Authorization': "Bearer {}".format(jwt)}
    response = requests.get(url,headers=header)
    return response