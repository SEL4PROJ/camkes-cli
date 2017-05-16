import os
import jinja2

from . import common

def make_subparser(subparsers):
    parser = subparsers.add_parser('procedure', description="Add an procedure")
    parser.add_argument('name', help="Name of procedure", type=str)
    parser.set_defaults(func=handle_procedure)
    common.add_argument_edit(parser)

def handle_procedure(args):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(common.part_template_path()))
    template = env.get_template("procedure.camkes")

    procedure_file_name = "%s.camkes" % args.name
    procedure_path = os.path.join(common.procedure_path(), procedure_file_name)

    if os.path.exists(procedure_path):
        args.logger.info("Procedure already exists")
    else:

        try:
            os.makedirs(os.path.dirname(procedure_path))
        except OSError:
            pass

        with open(procedure_path, 'w') as f:
            procedure_string = template.render({"name": args.name})
            f.write(procedure_string)

        args.logger.info("Created empty procedure in %s" % procedure_path)
        args.logger.info("Assuming default paths, you can import it in a component with:"
                         "\n\nimport \"../../%s/%s\";" %
                         (common.procedure_dir(), procedure_file_name))

    if args.edit:
        common.spawn_editor(procedure_path)
