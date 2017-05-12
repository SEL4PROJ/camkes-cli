import multiprocessing
import toml

from . import common

def make_subparser(subparsers):
    parser = subparsers.add_parser('init', description="Initialize an existing project")
    parser.add_argument('--jobs', type=int, help="Number of threads to use when downloading code",
                            default=multiprocessing.cpu_count())
    parser.set_defaults(func=handle_init)

def handle_init(args):
    with open(common.markup_path()) as info_file:
        info = toml.load(info_file)

        args.logger.info("Downloading dependencies...")
        common.get_code(".", info["manifest_url"], info["manifest_name"], args.jobs)

        args.logger.info("Instantiating build templates...")
        common.instantiate_build_templates(".", info)

        args.logger.info("Creating build system symlinks...")
        common.make_symlinks(".", info)
