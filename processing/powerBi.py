import json
from six import iteritems
import requests


def nested_lookup(key, document):
    """Lookup a key in a nested document, return a list of values"""
    return list(_nested_lookup(key, document))

def _nested_lookup(key, document):
    """Lookup a key in a nested document, yield a value"""
    if isinstance(document, list):
        for d in document:
            for result in _nested_lookup(key, d):
                yield result

    if isinstance(document, dict):
        for k, v in iteritems(document):
            if key == k or (key.lower() in k.lower()):
                yield v

            if isinstance(v, dict):
                for result in _nested_lookup(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in _nested_lookup(key, d): 
                        yield result

def strip_json(data, key):
    """ 
    Strips away all keys-value pair from the data dictionary 
    except for key 

    Parameters: 
        data:   Data from the Sesam pipe
        key:    The key we wish to save

    Returns:
        A dictionary with the specified key and its 
        corresponding values only
    """


    try:
        data = nested_lookup(key, data)[0]
    except IndexError:
        return data
    return data

def setup_table(Sesam_data):
    """ 
    Creates a new dictionary with the standard Power BI setup
    with one dataset and one table 

    Parameters:
        pipe_data: The data from the Sesam pipe

    Returns: 
        A new dictionary for Power BI use
    """

    new_table = {}
    new_table['name'] = Sesam_data['_id']
    new_table["defaultMode"] = "Push"
    new_table['tables'] = []
    new_table['tables'].append({})
    new_table['tables'][0]['name'] = Sesam_data['_id'] 
    new_table['tables'][0]['columns'] = []
    return new_table


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
            print(1)
            return False, None

    if len(current_datasets['value']) == 0:
        print(2)
        print(current_datasets)

        return False, None
    
    for existing_dataset in current_datasets['value']:
        if existing_dataset['name'] == new_dataset_name:
            return True, existing_dataset['id']
        else:
            print(3)

            return False, None

def add_columns(new_dict, Sesam_data, headers):
    """
    Fills in the columns in the disctionary from setup_powerBi_json
    with Sesam entities as rows, and values as columns 

    Parameters:
        new_dict: The dictionary created in setup_powerBi_json
        Sesam_data:     The data from Sesam

    Returns:
        A dictionary with the Sesam data attached in Power BI format
    """


    num_cols = len(Sesam_data[0].keys())
    col_keys = list(Sesam_data[0].keys())
    # TODO check if all entities has same amount of keys

    for col in range(num_cols):
        new_dict['tables'][0]['columns'].append({})                                                       
        new_dict['tables'][0]['columns'][col]['name'] = col_keys[col]                                      

        new_dict['tables'][0]['columns'][col]['dataType'] = find_dataType(col_keys[col], Sesam_data[0][col_keys[col]])

    return new_dict

def add_rows(Sesam_data):
    rows = {}
    rows["rows"] = []
    num_cols = len(Sesam_data)
    for i in range(len(Sesam_data)):
        rows["rows"].append({})
        for j, key in enumerate(Sesam_data[i].keys()):
            rows["rows"][i][key] = Sesam_data[i][key]
        
    return rows

def find_dataType(key, value):
    """
    Method for sorting out the most obvious dataTypes for specification in Power BI

    Parameters:
        key:    The key used from the dictionary
        value:  The value associated with the key  

    Returns: 
        A string for dataType specification 
    """
    

    key = key.lower()
    if key == 'ssn':
        return 'Int64'
        
    if key == 'datetime':
        return 'dateTime' 

    if key == 'address' or key == 'adresse':
        return 'String'

    if len(value.split()) != 1:
        return 'String'

    if value.lower() == 'true' or value.lower() == 'false':
        return 'Boolean'
    try:
        eval(value)
    except NameError:
        return 'String'
    except TypeError:
        return 'String'

    if type(eval(value)) == int:
        return 'Int64'

    if type(eval(value)) == float:
        # TODO: Always return Decimal for float atm. Seems like the safest option rn
        return 'Decimal'

    return 'Datetime'


def strip_Sesam_data(Sesam_data):
    """
    Function that strips the initial data of unnecessary information

    Parameters:
        powerBi_json
    
    Returns:
        The stripped Sesam data
    """
    
    try:
        Sesam_data = strip_json(Sesam_data, 'effectives')
    except SyntaxError:
        Sesam_data = Sesam_data

    try:
        Sesam_data = strip_json(Sesam_data, 'entities')
    except SyntaxError:
        Sesam_data = Sesam_data

    return Sesam_data