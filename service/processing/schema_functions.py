def schema_with_id(schema, dataset_id):
    remade_schema = {}
    remade_schema["_id"] = str(dataset_id)
    remade_schema['info'] = schema
    return remade_schema

def merge_schemas(old_schema, new_schema):
    merged_schema = new_schema
    for old_property in old_schema:
        if old_property.get('name') not in [new_property.get('name') for new_property in new_schema]:    
            merged_schema.append(old_property)
    return merged_schema

def find_old_schema(schemas, dataset_id):
    if len(schemas) == 0:
        return None
    for schema in schemas:
        if schema["_id"] == dataset_id:
            return schema.get('info')
    return None
