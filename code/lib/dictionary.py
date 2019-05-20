

def fix_name_field(o):
    if isinstance(o, dict):
        result = {}
        for key in o:
            new_key = key.replace('.', r'\uff0E')
            result[new_key] = fix_name_field(o[key])
        return result
    if isinstance(o, list):
        result = []
        for value in o:
            result.append(fix_name_field(value))
        return result
    return o


def defix_name_field(o):
    if isinstance(o, dict):
        result = {}
        for key in o:
            new_key = key.replace(r'\uff0E', '.')
            result[new_key] = defix_name_field(o[key])
        return result
    if isinstance(o, list):
        result = []
        for value in o:
            result.append(defix_name_field(value))
        return result
    return o