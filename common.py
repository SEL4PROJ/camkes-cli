import os
import shutil
import subprocess

import jinja2
import pdb

class MissingTemplate(Exception):
    pass

class RootNotFound(Exception):
    pass

def markup_name():
    return "camkes.toml"

def markup_path():
    return os.path.join(find_root(), markup_name())

def config_dir():
    return "configs"

def config_path():
    return os.path.join(find_root(), config_dir())

def image_dir():
    return "images"

def image_path():
    return os.path.join(find_root(), image_dir())

def find_root():
    """Traverse from the current directory to the root directory
       looking for a directory containing a camkes markup file.
       Returns the path to the closest ancestor directory of the
       current directory containing such a file. Raises an
       exception if no such directory is found."""
    current_path = os.getcwd()
    while True:
        markup_path = os.path.join(current_path, markup_name())
        if os.path.exists(markup_path):
            return current_path

        next_path = os.path.dirname(current_path)
        if next_path == current_path:
            break
        current_path = next_path

    raise RootNotFound("Failed to locate %s" % markup_name())

def base_path():
    return os.path.dirname(__file__)

def base_template_path():
    return os.path.join(base_path(), 'base_templates')

def app_template_path():
    return os.path.join(base_path(), 'app_templates')

def build_template_path():
    return os.path.join(base_path(), 'build_templates')

def build_system_path():
    return os.path.join(find_root(), "sel4")

def build_config_path():
    return os.path.join(build_system_path(), ".config")

def build_images_path():
    return os.path.join(build_system_path(), "images")

def save_config(name):
    try:
        os.makedirs(os.path.join(find_root(), "configs"))
    except OSError:
        pass

    shutil.copyfile(build_config_path(), os.path.join(config_path(), name))

def load_config(name):
    shutil.copyfile(os.path.join(config_path(), name), build_config_path())

def list_configs():
    try:
        return os.listdir(config_path())
    except RootNotFound:
        return []

def copy_images(name):
    try:
        os.makedirs(os.path.join(image_path(), name))
    except OSError:
        pass

    for f in os.listdir(build_images_path()):
        try:
            os.remove(os.path.join(image_path(), name, f))
        except OSError:
            pass
        shutil.move(os.path.join(build_images_path(), f),
                    os.path.join(image_path(), name))

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
