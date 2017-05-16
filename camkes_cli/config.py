import subprocess

from . import common

def make_subparser(subparsers):
    parser = subparsers.add_parser('config', description="Select a configuration")
    parser.add_argument('config', help="Name to associate with configuration", type=str,
                        choices=common.list_configs())
    parser.set_defaults(func=handle_config)

def handle_config(args):
    common.load_config(args.config)
