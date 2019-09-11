def max_entities_exceeded(entities):
	if len(entities) > 10000:
		return True
	else:
		return False
def max_properties_exceeded(properties):
	if len(properties) > 75:
		return True
	else:
		return False
