import shutil

import toml

from . import common

def make_subparser(subparsers):
    parser = subparsers.add_parser('update', description="Update build system")
    parser.set_defaults(func=handle_update)

def handle_update(args):
    args.logger.info("Deleting old build system path")
    shutil.rmtree(common.build_system_path())

    with open(common.markup_path()) as info_file:
        info = toml.load(info_file)
        common.init_build_system(args.logger, common.find_root(), info, args.jobs)
