import json
from six import iteritems
import numpy as np

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

def setup_powerBi_json(pipe_data):
    """ 
    Creates a new dictionary with the standard Power BI setup
    with one dataset and one table 

    Parameters:
        pipe_data: The data from the Sesam pipe

    Returns: 
        A new dictionary for Power BI use
    """
    new_dict = {}
    new_dict['name'] = pipe_data['_id']                                                                 # assume same name as the pipe
    new_dict['tables'] = {}
    new_dict['tables']['name'] = pipe_data['_id']                                                       # assume same name as the pipe
    new_dict['tables']['columns'] = []
    return new_dict

def make_new_json(new_dict, data):
    """
    Fills in the columns in the disctionary from setup_powerBi_json
    with Sesam entities as rows, and values as columns 

    Parameters:
        new_dict: The dictionary created in setup_powerBi_json
        data:     The data from Sesam

    Returns:
        A dictionary with the Sesam data attached in Power BI format
    """

    num_rows = len(data)
    num_cols = len(data[0].keys())
    col_keys = list(data[0].keys())
    # TODO check if all entities has same amount of keys

    for col in range(num_cols):
        new_dict['tables']['columns'].append({})                                                       
        new_dict['tables']['columns'][col]['name'] = col_keys[col]                                      
        
        for row in range(num_rows):         
            new_dict['tables']['columns'][col][data[row]['_id']] = data[row][col_keys[col]]

        new_dict['tables']['columns'][col]['dataType'] = find_dataType(col_keys[col], data[row][col_keys[col]])
    return new_dict

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
        return 'String'
        
    if key == 'datetime':
        return 'dateTime' 

    if key == 'address' or key == 'adresse':
        return 'String'

    if len(value.split()) != 1:
        return 'String'

    if value == 'True' or value == 'False':
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

def make_PowerBi_json(powerBi_json):
    """
    Function that calls all the other methods in the powerBI-script

    Parameters:
        powerBi_json
    """
    new_dict = setup_powerBi_json(powerBi_json)
        
    try:
        powerBi_json = strip_json(powerBi_json, 'effectives')
    except SyntaxError:
        powerBi_json = powerBi_json

    try:
        powerBi_json = strip_json(powerBi_json, 'entities')
    except SyntaxError:
        powerBi_json = powerBi_json

    powerBi_json = make_new_json(new_dict, powerBi_json)


    return powerBi_json