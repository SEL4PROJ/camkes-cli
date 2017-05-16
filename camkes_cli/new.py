import sys
import os
import multiprocessing
import collections

import toml
import jinja2

from . import common
from . import defaults

class DirectoryExists(Exception):
    pass

class TemplateParseError(Exception):
    pass

def make_skeleton(args):
    os.mkdir(args.directory)
    os.mkdir(os.path.join(args.directory, "src"))

def instantiate_base_templates(directory, info):

    templates_destinations = {
        "gitignore": ".gitignore",
        "app.camkes": "src/%s.camkes" % info["name"],
        "Makefile": "src/Makefile",
        "Kbuild": "src/Kbuild",
        "Kconfig": "src/Kconfig",
        "config_x86": "configs/x86",
        "config_x86_64": "configs/x86_64",
        "config_aarch32": "configs/aarch32",
    }

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(common.base_template_path()))

    for source in templates_destinations:
        try:
            template = env.get_template(source)
        except jinja2.exceptions.TemplateNotFound:
            raise common.MissingTemplate("Missing template \"%s\"" % source)

        output = template.render(info)

        dst = os.path.join(directory, templates_destinations[source])

        try:
            os.makedirs(os.path.dirname(dst))
        except OSError:
            pass

        with open(dst, 'w') as outfile:
            outfile.write(output)

def instantiate_app_template(template, directory, info):

    template_path = os.path.join(common.app_template_path(), template)

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))
    try:
        top_level_template = env.get_template("app.camkes")
    except jinja2.exceptions.TemplateNotFound:
        raise common.MissingTemplate("Missing template \"app.camkes\"")

    with open(os.path.join(directory, "src", info["name"] + ".camkes"), 'w') as outfile:
        outfile.write(top_level_template.render(info))

    base_path_source = os.path.join(template_path, "src")
    base_path_destintaion = os.path.join(directory, "src")
    for (path, _, files) in os.walk(base_path_source):

        for f in files:

            # omit hidden files
            if f.startswith('.'):
                continue

            rel = os.path.relpath(os.path.join(path, f), base_path_source)
            try:
                template = env.get_template(os.path.join("src", rel))
            except jinja2.exceptions.TemplateNotFound:
                raise common.MissingTemplate("Missing template \"%s\"" % rel)

            destination_file = os.path.join(base_path_destintaion, rel)
            try:
                os.makedirs(os.path.dirname(destination_file))
            except OSError:
                pass
            with open(destination_file, 'w') as outfile:
                outfile.write(template.render(info))

def make_subparser(subparsers):
    parser = subparsers.add_parser('new', description="Create a new project")
    parser.add_argument('name', help="Name of project", type=str)
    parser.add_argument('--directory', type=str, help="Alternative name of project directory",
                        default=None)
    parser.add_argument('--manifest_url', type=str, help="Base repo manifest",
                            default=defaults.CAMKES_MANIFEST_URL)
    parser.add_argument('--manifest_name', type=str, help="Base repo name",
                            default=defaults.CAMKES_MANIFEST_NAME)
    parser.add_argument('--template', type=str, help="Name of template to instantiate", nargs="?")
    parser.set_defaults(func=handle_new)
    common.add_argument_jobs(parser)

def make_info(args):
    return collections.OrderedDict([
        ("name", args.name),
        ("manifest_url", args.manifest_url),
        ("manifest_name", args.manifest_name),
    ])
def handle_new(args):
    if args.directory is None:
        args.directory = args.name

    if os.path.exists(args.directory):
        raise DirectoryExists("Directory \"%s\" already exists" % args.directory)

    info = make_info(args)

    args.logger.info("Creating directories...")
    make_skeleton(args)

    args.logger.info("Instantiating base templates...")
    instantiate_base_templates(args.directory, info)

    if args.template is not None:
        args.logger.info("Instantiating app template...")
        instantiate_app_template(args.template, args.directory, info)

    common.init_build_system(args.logger, args.directory, info, args.jobs)

    with open(os.path.join(args.directory, "camkes.toml"), 'w') as info_file:
        toml.dump(info, info_file)

    args.logger.info("Finished setting up new project \"%s\" in directory \"%s\"" % (args.name, args.directory))
