import re
from json import loads

def param_check(key:str,value:str)-> dict:

    if not re.findall('[\S]+', value, re.IGNORECASE):
        return {key:loads('null')}
    value  = value.replace('\'', '"')
    value =  value.replace('\r\n', '')
    return {key: loads(value)}

def convert_doc(method):
    method_doc = method.__doc__

    if method_doc is None:
        raise AssertionError(
            f'{type(method)}.{method.__name__}.__doc__ atribute is  empty')
    else:
        # TODO this regex have some limitations,
        #  it lead  necessity use loops for processing __doc__

        param_pattern = re.compile(
            r'((?<=:param )([\w\d ]+(?=:))([: ]+)([\d\w\s{}\'\":,\[\]\.]*(?=:param)))',
            re.IGNORECASE)
        param_pre_pattern = re.compile(
            r'((?<=:param )([\w\d ]+(?=:))([: ]+)([\d\w\s{}\'\":,\[\]\.]*(?=:return)))',
            re.IGNORECASE)
        return_pattern = re.compile(
            '(?<=:return: )(?:[\d\w\s{}\'\":,\[\]]*(?=:required)|[\d\w\s{}\'\":,\[\]]*)',
            re.IGNORECASE)

        # Line 'Require' all time must be at the end of __doc__
        return_require = re.compile(r"(?<=:required:)([\d\w\s{}\'\":,\[\]]*)",
                                    re.IGNORECASE)

        pos = 0
        arguments = dict()
        while True:
            param = param_pattern.search(method_doc, pos)
            if param is None:
                param = param_pre_pattern.search(method_doc, pos)
                if param is None:
                    break
                else:
                    _, arg_name, _, arg = param.groups()
                    arguments.update(param_check(arg_name, arg))
                    break

            else:
                _, arg_name, _, arg = param.groups()
                arguments.update(param_check(arg_name, arg))
                pos = param.span()[1]

        method_return = return_pattern.findall(method_doc)
        if method_return != []:
            try:
                output = loads(method_return[0].replace('\'', '"'))
            except Exception:
                # TODO add traceback of error
                raise AssertionError(f'{type(method)}.{method.__name__}._have unexpected format of __doc__')
        else:
            output = None


        require = return_require.findall(method_doc)
        if require and re.findall('[\S]+', require[0], re.IGNORECASE):
            require = loads(require[0])
        else:
            require = None

        return arguments, output, require


if __name__ == '__main__':
    print('Hello world')
    import sys, os
    sys.path.insert(0, '/home/user/projects/python_pr_relations_nlp/code')
    #print(sys.path)
    os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-1.8.0-openjdk-amd64"
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'newsAPI.settings')
    from django import setup
    setup()