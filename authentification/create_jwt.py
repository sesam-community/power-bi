import requests
import json
import adal

def get_token(client_id, tenant_id, refresh_token):
    """
    Authenticate using service principal w/ key.
    """
    authority_host_uri = 'https://login.microsoftonline.com'
    authority_uri = authority_host_uri + '/' + tenant_id
    resource_uri = 'https://analysis.windows.net/powerbi/api'

    context = adal.AuthenticationContext(authority_uri, api_version=None)
    access_token = context.acquire_token_with_refresh_token(refresh_token, client_id, resource_uri)
    return access_token