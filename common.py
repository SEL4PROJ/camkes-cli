import os
import shutil
import subprocess

import jinja2

class MissingTemplate(Exception):
    pass

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

def list_configs():
    return os.listdir("configs")

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

def get_code(directory, manifest_url, manifest_name, njobs):

    try:
        os.makedirs(os.path.join(directory, "sel4"))
    except OSError:
        pass

    cwd = os.getcwd()
    os.chdir(os.path.join(directory, "sel4"))
    subprocess.call(['repo', 'init', '-u', manifest_url, '-m', manifest_name])
    subprocess.call(['repo', 'sync', '--jobs', str(njobs)])
    os.chdir(cwd)

def instantiate_build_templates(directory, info):
    template_path = build_template_path()
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))

    for (path, _, files) in os.walk(template_path):
        for f in files:

            # omit hidden files
            if f.startswith('.'):
                continue

            rel = os.path.relpath(os.path.join(path, f), template_path)
            dest_path = os.path.join(directory, rel)

            try:
                template = env.get_template(rel)
            except jinja2.exceptions.TemplateNotFound:
                raise MissingTemplate("Missing template \"%s\"" % rel)

            try:
                os.remove(dest_path)
            except OSError:
                pass

            try:
                os.makedirs(os.path.dirname(dest_path))
            except OSError:
                pass

            with open(dest_path, 'w') as outfile:
                outfile.write(template.render(info))

def make_symlinks(directory, info):
    src = os.path.join(directory, 'src')
    dst = os.path.join(directory, 'sel4', 'apps')
    cwd = os.getcwd()
    os.chdir(dst)
    os.symlink(os.path.relpath(src, dst), info["name"])
    os.chdir(cwd)
