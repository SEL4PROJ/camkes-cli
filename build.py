import subprocess

import common

def make_subparser(subparsers):
    parser = subparsers.add_parser('build', description="Build the app")
    parser.add_argument('config', help="Name of configuration to build", type=str)
    parser.add_argument('--jobs', '-j', type=int, help="Number of threads to use",
                        default=1)
    parser.set_defaults(func=handle_build)

def handle_build(args):
    common.load_config(args.config)
    subprocess.call(['make', '-C', common.build_system_path(), '--jobs', str(args.jobs)])
    common.copy_images(args.config)
