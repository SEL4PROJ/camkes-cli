import sys
import os
import common
import shutil
import subprocess
import jinja2
import multiprocessing
import pdb

import defaults

class MissingTemplate(Exception):
    pass

class DirectoryExists(Exception):
    pass

class TemplateParseError(Exception):
    pass

def make_skeleton(args):
    os.mkdir(args.directory)
    os.mkdir(os.path.join(args.directory, 'src'))
    os.mkdir(os.path.join(args.directory, 'sel4'))

def instantiate_base_templates(args):

    templates_destinations = {
        "gitignore": ".gitignore",
        "app.camkes": "src/%s.camkes" % args.name,
        "Makefile": "src/Makefile",
        "Kbuild": "src/Kbuild",
        "Kconfig": "src/Kconfig",
    }

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(common.base_template_path()))

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

def maybe_instantiate_template(args):
    if args.template is None:
        return

    args.logger.info("Instantiating template: %s" % args.template)
    template_path = os.path.join(common.template_path(), args.template)

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))
    try:
        top_level_template = env.get_template("app.camkes")
    except jinja2.exceptions.TemplateNotFound:
        raise MissingTemplate("Missing template \"app.camkes\"")

    with open(os.path.join(args.directory, "src", args.name + ".camkes"), 'w') as outfile:
        outfile.write(top_level_template.render())

    base_path_source = os.path.join(template_path, "src")
    base_path_destintaion = os.path.join(args.directory, "src")
    for (path, _, files) in os.walk(base_path_source):

        for f in files:

            rel = os.path.relpath(os.path.join(path, f), base_path_source)
            pdb.set_trace()
            try:
                template = env.get_template(os.path.join("src", rel))
            except jinja2.exceptions.TemplateNotFound:
                raise MissingTemplate("Missing template \"%s\"" % rel)

            destination_file = os.path.join(base_path_destintaion, rel)
            try:
                os.makedirs(os.path.dirname(destination_file))
            except OSError:
                pass
            with open(destination_file, 'w') as outfile:
                outfile.write(template.render())

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

def make_subparser(subparsers):
    parser_new = subparsers.add_parser('new', description="Create a new project")
    parser_new.add_argument('name', help="Name of project", type=str)
    parser_new.add_argument('--directory', type=str, help="Alternative name of project directory", nargs="?")
    parser_new.add_argument('--manifest_url', type=str, help="Base repo manifest",
                            default=defaults.CAMKES_MANIFEST_URL)
    parser_new.add_argument('--manifest_name', type=str, help="Base repo name",
                            default=defaults.CAMKES_MANIFEST_NAME)
    parser_new.add_argument('--jobs', type=int, help="Number of threads to use when downloading code",
                            default=multiprocessing.cpu_count())
    parser_new.add_argument('--template', type=str, help="Name of template to instantiate", nargs="?")
    parser_new.set_defaults(func=handle_new)

def handle_new(args):
    if args.directory is None:
        args.directory = args.name

    if os.path.exists(args.directory):
        raise DirectoryExists("Directory \"%s\" already exists" % args.directory)

    args.logger.info("Creating directories...")
    make_skeleton(args)
    args.logger.info("Instantiating base templates...")
    instantiate_base_templates(args)
    args.logger.info("Downloading dependencies...")
    get_code(args)
    maybe_instantiate_template(args)
    make_symlinks(args)
    args.logger.info("Finished setting up new project \"%s\" in directory \"%s\"" % (args.name, args.directory))
