import argparse
import pathlib

from .utils.common import check_program, goto_workspace


def args(parser: argparse.ArgumentParser):
    """
    Adds the arguments for the run subcommand to the parser.

    NOTE: This is called from main.py.
    """
    from pathvalidate.argparse import validate_filename_arg, validate_filepath_arg

    parser.add_argument('name', type=validate_filename_arg,
                        help='The name of the workspace')
    parser.add_argument('--dry-run', action='store_true', default=False,
                        help='Print the command instead of running it')
    parser.add_argument('--disk-name', type=validate_filename_arg, default='disk.img',
                        help='The name of the disk image')
    parser.add_argument('--smp', type=int, default=2,
                        help='The number of virtual CPUs to use')
    parser.add_argument('--ram', type=int, default=4,
                        help='The amount of RAM to allocate in GB')
    parser.add_argument('--ssh-port', type=int, default=8022,
                        help='The port to forward SSH to')
    parser.add_argument('-Q', '--qemu-path', type=validate_filepath_arg,
                        help='The path to the QEMU executable')
    parser.add_argument('--qemu-debug', action='store_true',
                        help='Debug QEMU')
    parser.add_argument('-K', '--kernel', type=validate_filename_arg,
                        help='The name of the kernel image')
    parser.add_argument('-A', '--kernel-extra-bootargs', type=str,
                        help='Extra boot arguments to pass to the kernel')


def do(arch: str, **kwargs):
    """
    The entry point for the run subcommand. Just dispatches to the appropriate function
    based on the architecture.

    NOTE: This is called from main.py.
    """
    eval(f'do_{arch}')(**kwargs)


def do_aarch64(name: str,
               dry_run: bool,
               disk_name: str,
               smp: int,
               ram: int,
               ssh_port: int,
               qemu_path: str | None = None,
               qemu_debug: bool = False,
               kernel: str | None = None,
               kernel_extra_bootargs: str | None = None,
               extra: tuple[str] | None = None):
    from .utils.qemu import run_aarch64_linux as run

    qemu_extra_args = extra

    if qemu_path:
        qemu_path = pathlib.Path(qemu_path).resolve()
    goto_workspace('aarch64', name)
    qemu = check_program('qemu-system-aarch64', path=qemu_path)
    if not pathlib.Path(disk_name).exists():
        raise FileNotFoundError(
            'Disk image not found, please run `init` first')

    if kernel is not None:
        if not pathlib.Path(kernel).exists():
            candidate = pathlib.Path(f'Image-{kernel}')
            if not candidate.exists():
                raise FileNotFoundError(f'Kernel image `{kernel}` not found')
            kernel = candidate

    run(
        qemu,
        qemu_extra_args,
        init=False,
        smp=smp,
        ram=ram,
        disk=pathlib.Path(disk_name),
        ssh_port=ssh_port,
        qemu_debug=qemu_debug,
        kernel=kernel,
        kernel_extra_bootargs=kernel_extra_bootargs,
        dry_run=dry_run,
    )
