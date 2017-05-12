import os

from . import common

def list_templates():
    return os.listdir(common.base_template_path())

def make_subparser(subparsers):
    parser = subparsers.add_parser('info', description="Get information")
    parser.add_argument('--list_templates', help="List available templates",
                            action='store_true')
    parser.set_defaults(func=handle_info)

def handle_info(args):

    if args.list_templates:
        for t in os.listdir(common.app_template_path()):
            args.logger.info(t)
