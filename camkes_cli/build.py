import subprocess

from . import common
from . import clean

def make_subparser(subparsers):
    parser = subparsers.add_parser('build', description="Build the app")
    parser.add_argument('config', help="Name of configuration to build", type=str,
                        choices=common.list_configs())
    parser.set_defaults(func=handle_build)
    common.add_argument_jobs(parser)

def handle_build(args):
    if common.config_changed(args.config):
        args.__dict__['mrproper'] = False
        clean.handle_clean(args)

    common.load_config(args.config)
    subprocess.call(['make', '-C', common.build_system_path(), '--jobs', str(args.jobs)])
    common.copy_images(args.config)
