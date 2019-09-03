How to:
First, upload the microservice as a Sesam system. Go into your Sesam node and  


Run the get_refresh_token.py by the following command:

./get_refresh_token.py --tenant_id <tenant_id> --client_id <tenant_id> --resource 'https://analysis.windows.net/powerbi/api'

and follow the instructions from the terminal
next step would be to create a different bot/app user. More info on this to come.

Sinks in Sesam need to state "url": "/get_sesam/<node-id>/<pipe_name>" where <pipe_name> is the name of the sink. The pipe_name specifies where the schema will be retrieved from, as well as the name of the dataset in Power BI.

