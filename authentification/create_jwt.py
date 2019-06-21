import requests
import adal

def authenticate_client_key():
    """
    Authenticate using service principal w/ key.
    """
    authority_host_uri = 'https://login.microsoftonline.com'
    tenant = '<TENANT>'
    authority_uri = authority_host_uri + '/' + tenant
    resource_uri = 'https://management.core.windows.net/'
    client_id = '<CLIENT_ID>'
    client_secret = '<CLIENT_SECRET>'

    context = adal.AuthenticationContext(authority_uri, api_version=None)
    mgmt_token = context.acquire_token_with_client_credentials(resource_uri, client_id, client_secret)
    credentials = AADTokenCredentials(mgmt_token, client_id)

    return credentials


def get_access_token(application_id, application_secret, user_id, user_password, tenant_id):
    data = {
        'grant_type': 'password',
        'scope': 'openid',
        'resource': "https://analysis.windows.net/powerbi/api",
        'client_id': application_id,
        'client_secret': application_secret,
        'tenant': tenant_id
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