# -*- coding: utf-8 -*-
# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import absolute_import, print_function

from conda.base.context import context
from conda.misc import clone_env
from conda.cli.conda_argparse import ArgumentParser
from conda.cli import install
from conda import misc

from argparse import Namespace, RawDescriptionHelpFormatter
from os.path import join
import os
import textwrap

import conda.cli.main_remove
from conda.cli.conda_argparse import add_output_and_prompt_options, add_parser_prefix
from . import main_remove
from .common import find_prefix_name
from ..env import from_environment
from ..exceptions import CondaEnvException

DESCRIPTION = "Renames a conda environment."
EXAMPLE = """

Examples:

    conda env rename --name FOO BAR
    conda env rename --prefix /path/to/env BAR
    conda env rename -n FOO BAR
    conda env rename -p /path/to/env BAR

"""


def configure_parser(sub_parsers):
    p = sub_parsers.add_parser(
        'rename',
        formatter_class=RawDescriptionHelpFormatter,
        description=DESCRIPTION,
        epilog=EXAMPLE,
    )

    add_parser_prefix(p)
    add_output_and_prompt_options(p)

    p.add_argument("destination", nargs=1, help="New name for conda environment.")
    p.set_defaults(func='.main_rename.execute')


def execute(args, parser: ArgumentParser):
    dest = args.destination[0]  # this gets the "destination" name specified by the user in the command
    name = args.name
    prefix = args.prefix
    if name:
        print(name)
        # prefix = "?"  # get the prefix of the named env, somehow
    else:
        print(prefix)

    clone_env((name if name else prefix), dest)
    # the above clone_env() function is from conda/misc.py and currently only does a
    # "prefix to prefix" clone vs "name to name" etc

    # env = from_environment(name, prefix)

    # main_remove.execute(old_env, parser)
