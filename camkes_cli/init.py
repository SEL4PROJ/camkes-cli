import multiprocessing
import toml

from . import common

def make_subparser(subparsers):
    parser = subparsers.add_parser('init', description="Initialize an existing project")
    parser.set_defaults(func=handle_init)
    common.add_argument_jobs(parser)

def handle_init(args):
    with open(common.markup_path()) as info_file:
        info = toml.load(info_file)
        common.init_build_system(args.logger, common.find_root(), info, args.jobs)
