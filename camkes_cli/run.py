import subprocess
from elftools.elf.elffile import ELFFile

from . import common
from . import build

class UnknownArch(Exception):
    pass

class MissingKernel(Exception):
    pass

ELFTOOLS_ARCH_TABLE = {
    "x86": "x86",
    "x64": "x86_64",
    "ARM": "aarch32",
}


def make_subparser(subparsers):
    parser = subparsers.add_parser('run', description="Run the app in qemu")
    parser.add_argument('config', help="Name of configuration to run", type=str,
                        choices=common.list_configs())
    parser.add_argument('--plat', help="Name of platform (passed to qemu with -M)", default="kzm")
    parser.set_defaults(func=handle_run)
    common.add_argument_jobs(parser)

def handle_run(args):
    build.handle_build(args)

    app, maybe_kernel = common.app_image_paths(args.config)

    with open(app, 'rb') as f:
        elftools_arch_name = ELFFile(f).get_machine_arch()
        try:
            arch_name = ELFTOOLS_ARCH_TABLE[elftools_arch_name]
        except KeyError:
            raise UnknownArch("elftools reported unknown arch name: %s" % elftools_arch_name)

    args.logger.info("Found image for arch: %s" % arch_name)
    RUNFN_TABLE[arch_name](app, maybe_kernel, args)

def run_x86(app, kernel, args):
    if kernel is None:
        raise MissingKernel("Kernel image is missing")

    subprocess.call(['qemu-system-i386', '-cpu', 'Haswell', '-m', '512', '-nographic',
                     '-kernel', kernel, '-initrd', app])

def run_x86_64(app, kernel, args):
    if kernel is None:
        raise MissingKernel("Kernel image is missing")

    subprocess.call(['qemu-system-x86_64', '-cpu', 'Haswell', '-m', '512', '-nographic',
                     '-kernel', kernel, '-initrd', app])

def run_aarch32(app, kernel, args):
    subprocess.call(['qemu-system-arm', '-M', args.plat, '-nographic', '-kernel', app])

RUNFN_TABLE = {
    "x86": run_x86,
    "x86_64": run_x86_64,
    "aarch32": run_aarch32,
}
