import requests
import json
import datetime

"""
Base URL where to send token request
Placeholder contains Azure tenant id
"""
TOKEN_URL = "https://login.microsoftonline.com/{}/oauth2/v2.0/token"

"""
We use client_credentials flow with client_id and secret_id
Scope https://graph.microsoft.com/.default means app will have all permissions assigned to it 
in Azure Active Directory ( https://aad.portal.azure.com -> Dashboard -> App Registrations)
"""
TOKEN_REQUEST_PAYLOAD = data = {'grant_type': 'client_credentials',
                                'scope': 'https://graph.microsoft.com/.default'}

"""
Token cache
"""
__token_cache = {}


def add_token_to_cache(client_id, tenant_id, token_obj):
    """
    Function to add an access token for given client and tenant into token cache
    :param client_id:i d you get after register new app in Azure AD
    :param tenant_id: enant id may be found in Azure Admin Center -> Overview -> Properties
    :param token_obj: Oauth2 token object
    :return: None
    """
    __token_cache[client_id + tenant_id] = token_obj


def _get_token(client_id, client_secret, tenant_id):
    """
    Function for getting Oauth2 token by using clint_credentials grant type
    :param client_id: id you get after register new app in Azure AD
    :param client_secret: secret you get after register new app in Azure AD
    :param tenant_id: tenant id may be found in Azure Admin Center -> Overview -> Properties
    :return: oauth token object with timestamp added
    """
    token_url = TOKEN_URL.format(tenant_id)
    response = requests.post(token_url, data=data, verify=True, allow_redirects=False,
                             auth=(client_id, client_secret))
    response.raise_for_status()
    token_obj = json.loads(response.text)
    if not token_obj.get('access_token'):
        raise Exception("access_token not found in response")

    token_obj['timestamp'] = datetime.now()

    return token_obj


def _refresh_token(client_id, client_secret, tenant_id, r_token):
    """
    Function to refresh an Ouath2 token with refresh token
    :param client_id: id you get after register new app in Azure AD
    :param client_secret:  secret you get after register new app in Azure AD
    :param tenant_id: tenant id may be found in Azure Admin Center -> Overview -> Properties
    :param r_token: previously obtained refresh token
    :return: Oauth2 token object
    """
    token_url = TOKEN_URL.format(tenant_id)
    _data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default, offline_access',
        'grant_type': 'refresh_token',
        'refresh_token': r_token
    }
    response = requests.post(token_url, data=_data, verify=True, allow_redirects=False)
    response.raise_for_status()
    token_obj = json.loads(response.text)
    if not token_obj.get('access_token'):
        raise Exception("access_token not found in response")

    token_obj['timestamp'] = datetime.datetime.now()

    return token_obj


def get_token(client_id, client_secret, tenant_id):
    """
    Function to obtain Oauth token. This function search valid token in cache first and request it
    only when not found or if expired
    :param client_id: id you get after register new app in Azure AD
    :param client_secret: secret you get after register new app in Azure AD
    :param tenant_id: tenant id may be found in Azure Admin Center -> Overview -> Properties
    :return: oauth token object with timestamp added
    """
    token = __token_cache.get(client_id + tenant_id)
    ##ts = datetime.datetime.now()

    ##if not token or token['timestamp'] + token['expires_in'] + 5 < ts:
    ##    if 'refresh_token' in token:
    ##        r_token = token['refresh_token']
    ##        __token_cache[client_id + tenant_id] = _refresh_token(client_id, client_secret, tenant_id, r_token)
    ##    else:
    ##        __token_cache[client_id + tenant_id] = _get_token(client_id, client_secret, tenant_id)

    return __token_cache.get(client_id + tenant_id)