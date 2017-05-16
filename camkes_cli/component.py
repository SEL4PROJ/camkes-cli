import pdb
import os
import argparse
import importlib
import sys

import jinja2

from . import common

class Interface:
    def __init__(self, keyword, typ, name):
        self.keyword = keyword
        self.type = typ
        self.name = name
        self.ast = None

    def __repr__(self):
        return "%(interface)s %(type)s %(name)s" % self.__dict__

class InterfaceAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        keyword = option_string.strip('-')
        namespace.__dict__.setdefault("interfaces", [])\
            .append(Interface(keyword, *values))

def make_subparser(subparsers):
    parser = subparsers.add_parser('component', description="Add a component")
    parser.add_argument('name', help="Name of component", type=str)

    for iface in ['--provides', '--uses', '--emits', '--consumes', '--dataport']:
        parser.add_argument(iface, type=str, nargs=2, action=InterfaceAction,
                            default=[], metavar=('type', 'name'))

    parser.add_argument('--control', action='store_true')
    parser.add_argument('--hardware', action='store_true')

    parser.add_argument('--allow_missing_procedure', action='store_true')

    common.add_argument_edit(parser)
    parser.set_defaults(func=handle_component)

def handle_component(args):
    args.__dict__.setdefault("interfaces", [])

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(common.part_template_path()))
    def_template = env.get_template("component.camkes")
    src_template = env.get_template("component.c")
    component_dir_path = os.path.join(common.component_path(), args.name)
    component_def_path = os.path.join(component_dir_path, "%s.camkes" % args.name)
    component_src_path = os.path.join(component_dir_path, "src", common.component_src_filename())

    imports = []

    for interface in (i for i in args.interfaces if i.keyword == 'provides'):
        try:
            (procedure, path) = common.find_procedure(interface.type, args.logger)
        except common.MissingProcedure as e:
            if args.allow_missing_procedure:
                args.logger.warn("Can't find procedure definition for %s. "
                                 "Generated code will not compile." % args.name)
            else:
                raise e
            continue

        relpath = os.path.relpath(path, os.path.dirname(component_def_path))
        imports.append(relpath)

        #pdb.set_trace()
        interface.ast = procedure

    camkes_templates = common.camkes_templates_module()

    show_type = camkes_templates.macros.show_type

    def return_type(method):
        return show_type(method.return_type if method.return_type is not None else "void")

    def param_string(method):
        if len(method.parameters) == 0:
            return "void"

        c_types = []
        for p in method.parameters:
            c_type = show_type(p.type)
            if p.direction in ["refin", "out"]:
                c_type = "%s *" % c_type
            c_types.append(c_type)

        return ", ".join("%s %s" % (typ, name) for (typ, name) in
                         zip(c_types, (p.name for p in method.parameters)))

    def default_return(method):
        c_type = return_type(method)

        if c_type == "void":
            return ""

        if c_type.strip(" ").endswith("*"):
            value = "NULL"
        elif c_type in ["float", "double"]:
            value = "0.0"
        else:
            value = "0"

        return "\n    return %s;" % value

    ctx = {
        "name": args.name,
        "interfaces": args.interfaces,
        "control": args.control,
        "hardware": args.hardware,
        "imports": imports,
        "return_type": return_type,
        "param_string": param_string,
        "default_return": default_return,
    }

    if os.path.exists(component_def_path):
        args.logger.info("Component def already exists in %s" % component_def_path)
    else:
        try:
            os.makedirs(os.path.dirname(component_def_path))
        except OSError:
            pass

        with open(component_def_path, 'w') as f:
            f.write(def_template.render(ctx))
            args.logger.info("Created component def for %s in %s" %
                             (args.name, os.path.relpath(component_def_path, common.find_root())))

    if os.path.exists(component_src_path):
        args.logger.info("Component src already exists in %s" % component_src_path)
    else:
        try:
            os.makedirs(os.path.dirname(component_src_path))
        except OSError:
            pass

        with open(component_src_path, 'w') as f:
            f.write(src_template.render(ctx))
            args.logger.info("Created component src for %s in %s" %
                             (args.name, os.path.relpath(component_src_path, common.find_root())))

    args.logger.info("Assuming  default paths, you can import it in the top level file with:"
                     "\n\nimport \"%s\";" % os.path.relpath(component_def_path, common.src_path()))

    if args.edit:
        common.spawn_editor(component_src_path)
