import sys
import argparse
import logging
import pkg_resources

from . import common
from . import new
from . import init
from . import info
from . import menuconfig
from . import build
from . import clean

def init_logger():
    logger = logging.getLogger(__name__)

    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(ch)

    logger.setLevel(logging.INFO)

    return logger

def make_parser():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    new.make_subparser(subparsers)
    init.make_subparser(subparsers)
    info.make_subparser(subparsers)
    menuconfig.make_subparser(subparsers)
    build.make_subparser(subparsers)
    clean.make_subparser(subparsers)

    return parser

def main():
    args = make_parser().parse_args(sys.argv[1:])
    args.logger = init_logger()
    try:
        args.func(args)
    except new.DirectoryExists as e:
        args.logger.error(e)
    except common.MissingTemplate as e:
        args.logger.error(e)
    except new.TemplateParseError as e:
        args.logger.error(e)
    except common.RootNotFound as e:
        args.logger.error(e)
