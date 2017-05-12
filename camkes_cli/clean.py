import subprocess

from . import common

def make_subparser(subparsers):
    parser = subparsers.add_parser('clean', description="Delete generated object and binary files")
    parser.add_argument('--mrproper', action='store_true')
    parser.set_defaults(func=handle_clean)

def handle_clean(args):
    if args.mrproper:
        subprocess.call(['make', '-C', common.build_system_path(), 'mrproper'])
    else:
        subprocess.call(['make', '-C', common.build_system_path(), 'clean'])

