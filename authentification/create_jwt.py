import requests
import json
import adal

def get_token(client_id, client_secret, tenant_id):
    """
    Authenticate using service principal w/ key.
    """
    authority_host_uri = 'https://login.microsoftonline.com'
    authority_uri = authority_host_uri + '/' + tenant_id
    resource_uri = 'https://analysis.windows.net/powerbi/api'

    context = adal.AuthenticationContext(authority_uri, api_version=None)
    access_token = context.acquire_token_with_client_credentials(resource_uri, client_id, client_secret)
    return access_token