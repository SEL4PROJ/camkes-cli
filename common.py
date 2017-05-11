import os
import shutil

def base_path():
    return os.path.dirname(__file__)

def base_template_path():
    return os.path.join(base_path(), 'base_templates')

def app_template_path():
    return os.path.join(base_path(), 'app_templates')

def build_template_path():
    return os.path.join(base_path(), 'build_templates')

def build_system_path():
    return "sel4"

def build_config_path():
    return os.path.join(build_system_path(), ".config")

def build_images_path():
    return os.path.join(build_system_path(), "images")

def save_config(name):
    try:
        os.makedirs("configs")
    except OSError:
        pass

    shutil.copyfile(build_config_path(), os.path.join("configs", name))

def load_config(name):
    shutil.copyfile(os.path.join("configs", name), build_config_path())

def copy_images(name):
    try:
        os.makedirs(os.path.join("images", name))
    except OSError:
        pass

    for f in os.listdir(build_images_path()):
        try:
            os.remove(os.path.join("images", name, f))
        except OSError:
            pass
        shutil.move(os.path.join(build_images_path(), f), os.path.join("images", name))
