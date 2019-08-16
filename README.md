[![Build Status](https://travis-ci.org/sesam-community/power-bi.svg?branch=master)](https://travis-ci.org/sesam-community/power-bi)

# Power-BI-Connector

This is a microservice for connecting to the Power BI restAPI to Sesam and posting data for later visualization.
You need an Azure account to run this service.

## Limitations
The limitations for uploading data are:
 * 75 max columns
 * 1 max tables
 * 10.000 max batch_size
 * 1.000.000 entities added per hour per dataset
 * 5 max pending POST entities requests per dataset
 * 120 POST entities requests per minute per dataset
 * If table has 250.000 or more entities, 120 POST entities requests per hour per dataset
 * 5.000.000 max entitiesa stored per table
 * 4.000 characters per value for string column in POST entities operation## Example of Sesam sink config

## Register a web application with the Azure Active Directory admin center

1. Open a browser and navigate to the [Azure Active Directory admin center](https://aad.portal.azure.com).

2. Select **New registration**. On the **Register an application** page, set the values as follows.

    - Set **Name** to `<Some Nice Name>`.

3. Choose **Register**. On the **Name** page, copy the value of the **Application (client) ID** and save it, you will need it later.

4. Select **Certificates & secrets** under **Manage**. Select the **New client secret** button. Enter a value in **Description** and select one of the options for **Expires** and choose **Add**.

## Generate a refresh token for Power BI
Run the following line in your terminal under /service:
```
./get_refresh_token.py --tenant_id <your-tenant-id> --client_id <your-client-id> --resource 'https://analysis.windows.net/powerbi/api' 
```
The refresh token will be printed to terminal

## Example of Sesam system config
```
{
  "_id": "power-bi-ms",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "PBI-CLIENT-ID": "$SECRET(my-client-id)",
      "PBI-REFRESH-TOKEN": "$SECRET(my-refresh-token)",
      "SESAM-JWT": "$SECRET(my-jwt)",
      "TENANT-ID": "$SECRET(my-tenant-id)",
      "WORKSPACE-ID": "07852248-6e81-49b3-b0ac-8c9e9d8c881f"
    },
    "image": "sesamcommunity/power-bi:latest",
    "port": 5000
  },
  "verify_ssl": true
}
```
Add the secrets by entering the "Secrets" window in the Sesam system and select "add secret" with names as specified in the config. 
 * my-client-id: The client ID of your web application
 * PBI-refresh-token: The token generated when running get_refresh_token.py
 * my-sesam-jwt: The Sesam JWT generated by going into "Subscriptions" in settings in your Sesam node
 * my-tenant-id: Your Azure Tenant ID

In addition you need to specify the workspace ID in Power BI to which you wish to post the data

## Example of Sesam sink config
```
{
  "_id": "person-powerbi-endpoint",
  "type": "pipe",
  "source": {
    "type": "dataset",
    "dataset": "crm-person"
  },
  "sink": {
    "type": "json",
    "system": "power-bi-ms",
    "url": "/get_sesam/datahub-0b08b50b/person-powerbi-endpoint"
  },
  "pump": {
    "cron_expression": "0 0 * * ?",
    "rescan_run_count": 1
  },
  "batch_size": 10000,
  "checkpoint_interval": 10000
}
```
## Run program locally
To run main.py locally with some test data you need the following environment variables defined:
 * PBI-CLIENT-ID
 * TENANT-ID
 * PBI-REFRESH-TOKEN
 * WORKSPACE-ID
 The workspace id can be found in the url when inside your Power BI account.

The following adjustments need to be made in main_func in main.py:

Global variables:
 * Sesam_headers: comment out

Inside main_func:
 * Comment out entities
 * Specify entities manually as a list of dictionaries with self-specified key-value pairs
 * Comment out args
 * Specify a new args object by: args = {"is_first": True, "request_id": 1}
 * Comment out everything from the first response = requests.get.... call down to after the schema definition.
 * Specify schema manually. The schema should be a list of dictionaries where every dictionary has a property 'name' corresponding to the different properties in the entities. The dictionaries also need the property 'type' to specify what sort of data type the property contains. For test-environments, the easiest is just to put this to 'String'.
These are simple examples of test entities and the test schema:
```entities = [{"_id": 1, "name": "Erik", "age": 20},{"_id": 1, "name": "Ashkan", "age": 20},{"_id": 1, "name": "Jonas", "age": 20}]```
```schema = [{"name": "name", "type": "String"}, {"name": "age", "type": "String"}]``` 

Now run the program and type 0.0.0.0:5000/some_node_id/test_dataset.
The path 'some_data_hub' can be anything, since we do not connect to Sesam any more.
The path 'dest_dataset' is the name of the PowerBI dataset. This can be set to anything.