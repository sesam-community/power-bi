#!/usr/bin/env python3

import adal
import click
import os

@click.command()
@click.option('--auth_endpoint', default='https://login.microsoftonline.com', required=False)
@click.option('--tenant_id', required=True)
@click.option('--client_id', required=True)
@click.option('--resource', required=True)
def get_refresh_token(auth_endpoint, tenant_id, client_id, resource):
    context = adal.AuthenticationContext('/'.join([auth_endpoint, tenant_id]))
    user_code_info = context.acquire_user_code(resource, client_id);
    print(user_code_info.get('message'))
    res = context.acquire_token_with_device_code(resource, user_code_info, client_id)
    refresh_token = res.get('refreshToken')
    os.environ['PBI-REFRESH-TOKEN'] = refresh_token
    print(os.environ['REFRESH-TOKEN'])
if __name__ == '__main__':
    get_refresh_token()
