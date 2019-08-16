# Power-BI-Connector

This is a microservice for connecting to the Power BI restAPI to Sesam and posting data for later visualization

### Needed prerequisites to run the microservice:
 * flask
 * requests
 * adal
 * nose
 * six
 * click

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
    "image": "erikalev/power-bi:latest",
    "port": 5000
  },
  "verify_ssl": true
}
```
