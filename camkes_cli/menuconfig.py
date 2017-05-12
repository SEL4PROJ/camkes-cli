import subprocess

from . import common

def make_subparser(subparsers):
    parser = subparsers.add_parser('menuconfig', description="Configure build system")
    parser.add_argument('config', help="Name to associate with configuration", type=str)
    parser.set_defaults(func=handle_menuconfig)

def handle_menuconfig(args):
    try:
        common.load_config(args.config)
    except:
        pass
    subprocess.call(['make', '-C', common.build_system_path(), 'menuconfig'])
    common.save_config(args.config)
