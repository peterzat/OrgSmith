"""Command-line entry point: the stage verbs of python -m orgsmith.

M0 skeleton: verbs are registered as the pipeline stages land.
"""

import argparse

from . import PRODUCT_NAME, __version__


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="orgsmith",
        description=f"{PRODUCT_NAME}: generate synthetic organizations.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.parse_args(argv)
    parser.print_help()
    return 0
