import requests

## Setting helpers
application_id = "8df57daa-57e6-4044-9d3f-33aee3171de8"
application_secret = "AXov1dtKsZjakaxr0oh3zUiyVsRD3vwfBBgKwTSc3dE"
user_id = ""
user_password = ""
##

def get_access_token(application_id, application_secret, user_id, user_password):
    data = {
        'grant_type': 'password',
        'scope': 'openid',
        'resource': "https://analysis.windows.net/powerbi/api",
        'client_id': application_id,
        'client_secret': application_secret,
        'username': user_id,
        'password': user_password
    }
    token = requests.post("https://login.microsoftonline.com/common/oauth2/token", data=data)
    assert token.status_code == 200, "Fail to retrieve token: {}".format(token.text)
    print("Got access token: ")
    print(token.json())
    return token.json()['access_token']


def make_headers(application_id, application_secret, user_id, user_password):
    return {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': "Bearer {}".format(get_access_token(application_id, application_secret, user_id, user_password))
    }