import json
from six import iteritems
import requests
import sys


#tables = [Sesam_data_id, "dates"]
def setup_dataset(Sesam_data_id):
    """ 
    Creates a new dictionary with the standard Power BI setup
    with one dataset and one table 

    Parameters:
        pipe_data: The data from the Sesam pipe

    Returns: 
        A new dictionary for Power BI use
    """

    tables = [Sesam_data_id]
    new_dataset                = {}
    new_dataset['name']        = Sesam_data_id
    new_dataset["defaultMode"] = "Push"
    new_dataset['tables']      = []

    for i, table in enumerate(tables):
        new_dataset['tables'].append({})
        new_dataset['tables'][i]['name']    = table 
        new_dataset['tables'][i]['columns'] = []

    return new_dataset

def find_dataset_id(response, pipe_name):
    for dataset in response.json()['value']:
        print(dataset)
        if dataset['name'] == pipe_name:
            return dataset['id']
    print("No matching dataset was found")
    sys.exit()

def check_dataset_status(current_datasets, entities, pipe_name, update_rows, update_columns, new_dataset):
    try:
      num_keys_new = len(entities[0].keys())
    except IndexError:
      print("There are no entities in the Sesam data")
      sys.exit()

    try:
      current_datasets.json()['value']
      for dataset in current_datasets.json()['value']:
        if dataset['name'] == pipe_name:
          dataset_id = dataset['id'] 
          num_keys_old = len(current_datasets.json()['value'][0].keys())
          if num_keys_old == num_keys_new:
            update_rows = True
            break
          else:
            update_columns = True
            break
      if not update_columns and not update_rows:
        dataset_id = False
        new_dataset = True
    except KeyError:
      new_dataset = True
      dataset_id = False

    return update_rows, update_columns, new_dataset, dataset_id

def check_dataset(current_datasets, new_dataset_name):
    """
    Checks if the new dataset already exists in Power BI.
    
    Parameters:
        current_dataset: The existing datasets in Power BI
        new_dataset_name: The new dataset name
    Returns:
        True and the id of the dataset if the dataset already exists
        False and None if the dataset does not exist
    """
    
    try: 
        current_datasets['value']
    except KeyError:
        if current_datasets['name'] == new_dataset_name:
            return True, current_datasets['id']
        else:
            return False, None

    if len(current_datasets['value']) == 0:
        return False, None
    
    for existing_dataset in current_datasets['value']:
        if existing_dataset['name'] == new_dataset_name:
            return True, existing_dataset['id']
        else:
            return False, None


def add_columns(new_dict, entities, schema):
    """
    Fills in the columns in the disctionary from setup_powerBi_json
    with Sesam entities as rows, and values as columns 

    Parameters:
        new_dict: The dictionary created in setup_powerBi_json
        Sesam_data:     The data from Sesam

    Returns:
        A dictionary with the Sesam data attached in Power BI format
    """

    num_tables = len(new_dict['tables'])
    num_columns = len(schema)

    keys = [data['name'] for data in schema]
    for i in range(num_tables):
        for j in range(num_columns):
            try:
                dataType = schema[j]['type'].capitalize()
                if dataType == 'Null':
                    dataType = 'String'

            except IndexError:
                dataType = 'String'

            new_dict['tables'][i]['columns'].append({})                                                       
            new_dict['tables'][i]['columns'][j]['name'] = keys[j]
            if dataType == 'Datetime':
                new_dict['tables'][i]['columns'][j]['dataType'] = 'DateTime'
                new_dict['tables'][i]['columns'][j]['formatString'] = "m/d/yyyy"
                #new_dict['tables'][0]['columns'][col]['summarizeBy'] = "none"
            else:
                new_dict['tables'][i]['columns'][j]['dataType'] = dataType
    return new_dict, keys

def add_rows(entities, populated_dataset, keys):

    rows         = {}
    rows["rows"] = []
    num_rows     = len(entities)
    num_tables   = len(populated_dataset['tables'])

    for i in range(num_tables):
        for j, entity in enumerate(entities):
            rows["rows"].append({})
            for k, key in enumerate(keys):
                dataType = populated_dataset['tables'][i]['columns'][k]['dataType']
                try:
                    value = format_value(entity[key], dataType)
                except KeyError:
                    value = format_value("", dataType)
                rows['rows'][j][key] = value
    return rows

def format_value(value, dataType):
    if dataType == 'Boolean':
        value = str(value).capitalize()
        if value != 'False' and value != 'True':
            value = 'False' # default is missing value
        value = bool(value)
        return value

    if dataType == 'DateTime':
        print(value)
        split_value = value.split()
        if len(split_value) == 0:
            return "0000-00-00"

        if split_value[0][0] == '~':
            return value.split()[0][2:]
        else:
            return value

    if dataType == 'Decimal':
        if value == "":
            return "0.0"
        if str(value).split()[0][0] == '~':
            return str(value).split()[0][2:]
        else:
            return str(value)
    else:
        return str(value)