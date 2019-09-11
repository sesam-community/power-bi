[![Build Status](https://travis-ci.org/sesam-community/power-bi.svg?branch=master)](https://travis-ci.org/sesam-community/power-bi)

# Power-BI-Connector

This is a microservice for connecting to the Power BI restAPI to Sesam and posting data for later visualization.
You need an Azure account to run this service.

## Limitations
The Power BI API limitations for uploading data are:
 * 75 max columns
 * 1 max tables
 * 10.000 max batch_size
 * 1.000.000 entities added per hour per dataset
 * 5 max pending POST entities requests per dataset
 * 120 POST entities requests per minute per dataset
 * If table has 250.000 or more entities, 120 POST entities requests per hour per dataset
 * 5.000.000 max entitiesa stored per table
 * 4.000 characters per value for string column in POST entities operation## Example of Sesam sink config

Practically speaking when posting data from sesam, this means we are limited to datasets of 1.000.000 rows/entities, as we need to adopt a truncate-load pattern, and generally cannot wait 1 hour per 1.000.000 "batch".

## Register a web application with the Azure Active Directory admin center

1. Open a browser and navigate to the [Azure Active Directory admin center](https://aad.portal.azure.com).

2. Select **New registration**. On the **Register an application** page, set the values as follows.

    - Set **Name** to `<Some Nice Name>`.

3. Choose **Register**. On the **Name** page, copy the value of the **Application (client) ID** and save it, you will need it later.

4. Select **Certificates & secrets** under **Manage**. Select the **New client secret** button. Enter a value in **Description** and select one of the options for **Expires** and choose **Add**.

## Generate a refresh token for Power BI
Create a Sesam system by pasting in the config below into the config of the system.

## Example of Sesam system config
```
{
  "_id": "powerbi-ms",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "SESAM-JWT": "$SECRET(my-jwt)",
      "PBI-CLIENT-ID": "my-client-id",
      "TENANT-ID": "my-tenant-id",
      "SESAM-NODE-ID": "my-sesam-node-id",
      "WORKSPACE-ID": "my-powerbi-workspace-id"
    },
    "image": "sesamcommunity/power-bi:latest",
    "port": 5000
  },
  "verify_ssl": true
}

```
Add the SESAM_JWT secret by entering the "Secrets" window in the Sesam system and select "add secret" with names as specified in the config. 
For the other variables stated in the config paste in your personal values inside the quotation signs (""). 
 * my-client-id: The client ID of your web application
 * my-tenant-id: Your Azure Tenant ID
 * my-sesam-node-id: The text between "https://" and ".sesam.cloud/api" in the url above the node name and the "Overview" window inside your node.
 * my-powerbi-workspace-id: The workspace id in Power Bi shown after "groups/" in the url when logged into Power BI and inside a workspace.  

When running saving the config the microservice will run. Go to the "Status" section of the system and press "Refresh". There will be a line printed in the "Logs" window with instructions. When yuo have entered the code and logged in as instructed you will see a windows which telling you to close the window. Please close it.
Go back to the "Status" section of your system and press "Refresh" again. Your refresh token should now be shown in the "Log". Add it as a secret under the name 'my-refresh-token' and paste the following line under the "SESAM-JWT"-line:
```
  "PBI-REFRESH-TOKEN": "$SECRET(my-refresh-token)",
```
such that the config now reads 
```
{
  "_id": "power-bi-ms",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "PBI-CLIENT-ID": "31cb468e-3d61-4246-851f-e8162f8e0a44",
      "PBI-REFRESH-TOKEN": "$SECRET(my-refresh-token)",
      "SESAM-JWT": "$SECRET(my-jwt)",
      "SESAM-NODE-ID": "datahub-0b08b50b",
      "TENANT-ID": "7bcbcc45-fb12-41d3-8ace-fa0fffaebf1d",
      "WORKSPACE-ID": "07852248-6e81-49b3-b0ac-8c9e9d8c881f"
    },
    "image": "sesamcommunity/power-bi:latest",
    "port": 5000
  },
  "verify_ssl": true
}
```
After saving your system should now run by it self (go back to the "Status" section and press "Refresh").

NOTE: It might take a couple of seconds for the microservice to re-run. Just wait a couple of seconds and press "Refresh" again. 

The three pipes below shows how to send data into Power BI through the microservice in the new "powerbi-ms"-system. The first pipe ("person-powerbi") is where you transform your data. In this example we simply pass through all the data from "crm-person".

## Example of Sesam pipe 
```
{
  "_id": "person-powerbi",
  "type": "pipe",
  "source": {
    "type": "dataset",
    "dataset": "crm-person"
  },
  "transform": {
    "type": "dtl",
    "rules": {
      "default": [
        ["copy", "*"]
      ]
    }
  },
  "remove_namespaces": true
}

```

In this pipe ("person-powerbi-endpoint") we send the data into Power BI through the "powerbi-ms"-system. Set the batch-size to your preference (max 10.000). 
## Example of Sesam sink config
```
{
  "_id": "person-powerbi-endpoint",
  "type": "pipe",
  "source": {
    "type": "dataset",
    "dataset": "person-powerbi"
  },
  "sink": {
    "type": "json",
    "system": "powerbi-ms",
    "url": "/person-powerbi/person-powerbi-endpoint/my_table"
  },
  "transform": {
    "type": "dtl",
    "rules": {
      "default": [
        ["filter",
          ["eq", "_S._deleted", false]
        ],
        ["copy", "*"]
      ]
    }
  },
  "pump": {
    "cron_expression": "0 0 * * ?",
    "rescan_run_count": 1
  },
  "batch_size": 100,
  "checkpoint_interval": 100
}

```

The following pipe (powerbi-schemas) is needed to gather information about the last time you sent data through Sesam to Power BI. It's essential to conserve the integrity of your data inside Poewr BI. 
## Example of Sesam sink config
```
{
  "_id": "powerbi-schemas",
  "type": "pipe",
  "source": {
    "type": "http_endpoint"
  },
  "sink": {
    "type": "dataset",
    "dataset": "powerbi-schemas"
  },
  "transform": {
    "type": "dtl",
    "rules": {
      "default": [
        ["copy", "*"]
      ]
    }
  },
  "remove_namespaces": true
}

```