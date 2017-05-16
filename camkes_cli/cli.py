import sys
import os
import argparse
import logging

from . import common
from . import new
from . import init
from . import info
from . import menuconfig
from . import build
from . import clean
from . import update
from . import run
from . import config
from . import component
from . import procedure

def init_logger():
    logging.basicConfig(stream=open(os.devnull, 'w'))
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
    update.make_subparser(subparsers)
    run.make_subparser(subparsers)
    config.make_subparser(subparsers)
    component.make_subparser(subparsers)
    procedure.make_subparser(subparsers)

    return parser

APP_EXCEPTIONS = (
    new.DirectoryExists,
    common.MissingTemplate,
    new.TemplateParseError,
    common.RootNotFound,
    common.NoApp,
    common.MultipleApps,
    common.MultipleKernels,
    common.MissingProcedure,
    run.UnknownArch,
    run.MissingKernel,
)

def main():
    parser = make_parser()
    args = parser.parse_args(sys.argv[1:])
    args.logger = init_logger()
    try:
        if 'func' in args:
            args.func(args)
        else:
            parser.print_help()

    except APP_EXCEPTIONS as e:
        args.logger.error(e)
