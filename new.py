import sys
import os
import common
import shutil
import subprocess
import jinja2

class MissingTemplate(Exception):
    pass

class DirectoryExists(BaseException):
    pass

def make_skeleton(args):
    os.mkdir(args.directory)
    os.mkdir(os.path.join(args.directory, 'src'))
    os.mkdir(os.path.join(args.directory, 'sel4'))

def instantiate_templates(args):

    templates_destinations = {
        "gitignore": ".gitignore",
        "app.camkes": "src/%s.camkes" % args.name,
        "Makefile": "src/Makefile",
        "Kbuild": "src/Kbuild",
        "Kconfig": "src/Kconfig",
    }

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(common.template_path()))

    for source in templates_destinations:
        try:
            template = env.get_template(source)
        except jinja2.exceptions.TemplateNotFound:
            raise MissingTemplate("Missing template \"%s\"" % source)

        output = template.render(name=args.name)

        dst = os.path.join(args.directory, templates_destinations[source])

        try:
            os.makedirs(os.path.dirname(dst))
        except OSError:
            pass

        with open(dst, 'w') as outfile:
            outfile.write(output)


def get_code(args):
    cwd = os.getcwd()
    os.chdir(os.path.join(args.directory, 'sel4'))
    subprocess.call(['repo', 'init', '-u', args.manifest_url, '-m', args.manifest_name])
    subprocess.call(['repo', 'sync'])
    os.chdir(cwd)

def make_symlinks(args):
    src = os.path.join(args.directory, 'src')
    dst = os.path.join(args.directory, 'sel4', 'apps')
    cwd = os.getcwd()
    os.chdir(dst)
    os.symlink(os.path.relpath(src, dst), args.name)
    os.chdir(cwd)

def handle_new(args):
    if args.directory is None:
        args.directory = args.name

    if os.path.exists(args.directory):
        raise DirectoryExists("Directory %s already exists" % args.directory)

    args.logger.info("Creating directories...")
    make_skeleton(args)
    args.logger.info("Instantiating templates...")
    instantiate_templates(args)
    args.logger.info("Downloading dependencies...")
    get_code(args)

    make_symlinks(args)
    args.logger.info("Finished setting up new project \"%s\" in directory \"%s\"" % (args.name, args.directory))
