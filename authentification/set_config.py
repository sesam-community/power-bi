import os
import json

def set_environ(config_file):
	with open(config_file, "rb") as f:
		environ_vars = json.load(f)

	
	for key, value in environ_vars.items():
		if key != 'mappings':
			os.environ[key.upper()]= value
		else:
			return value