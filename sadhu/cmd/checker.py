import os
from .. import checker

def main():
    filename = os.environ.get('SADHU_SETTINGS', None)

    if filename is None:
        print('This program require SADHU_SETTINGS environment')
        return
    print(filename)

    settings = dict()
    with open(filename, mode='rb') as config_file:
        exec(compile(config_file.read(), filename, 'exec'), settings)

    settings.pop('__builtins__')

    checker_server = checker.Server(settings)

    checker_server.run()
   


