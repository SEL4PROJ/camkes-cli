import os

def base_path():
    return os.path.dirname(__file__)

def base_template_path():
    return os.path.join(base_path(), 'base_templates')
