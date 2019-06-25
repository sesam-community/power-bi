import json
from six import iteritems

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
    try:
        data = nested_lookup(key, data)[0]
    except IndexError:
        return data
    return data

def setup_powerBi_json(pipe_data):
    new_dict = {}
    new_dict['name'] = pipe_data['_id']
    new_dict['tables'] = {}
    new_dict['tables']['name'] = 'table_name'
    new_dict['tables']['columns'] = []


def powerBi_json_format(new_dict, data):
    
    new_dict = {}
    new_dict['name'] = 'dataset_name'
    new_dict['tables'] = {}
    new_dict['tables']['name'] = 'table_name'
    new_dict['tables']['columns'] = []

    num_rows = len(data)
    num_cols = len(data[0].keys())
    col_keys = list(data[0].keys())
    # TODO check if all entities has same amount of keys
    
    for i in range(num_cols):
        new_dict['tables']['columns'].append({})
        for j in range(num_rows):
            new_dict['tables']['columns'][i][col_keys[i]] = data[j][col_keys[i]]
            new_dict['tables']['columns'][i]['name'] = 'String'
            new_dict['tables']['columns'][i]['dataType'] = 'String'

    return new_dict