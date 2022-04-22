# -*- coding: utf-8 -*-
# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import absolute_import, print_function

from conda.misc import clone_env

from argparse import Namespace, RawDescriptionHelpFormatter
import os
import textwrap

from conda.cli.conda_argparse import add_output_and_prompt_options, add_parser_prefix

_help = "Rename an environment"
_description = _help + """

Renames a provided environment.
""".lstrip()

_example = """
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
        description=_description,
        help=_help,
        epilog=_example,
    )

    add_parser_prefix(p)
    add_output_and_prompt_options(p)

    p.set_defaults(func='.main_rename.execute')

# ^^ I tried to add "--name" and "--prefix" as additional flags here but since they already exist in
# conda/cli/conda_argparse.py it looks like we would just need to import/use those here somehow, kind of like
#

# conda_env/cli/main_remove.py module's "execute" function is below:
def execute(args, parser):
    if not (args.name or args.prefix):
        name = os.environ.get('CONDA_DEFAULT_ENV', False)
        prefix = os.environ.get('CONDA_PREFIX', False)
        if not (name or prefix):
            msg = "Unable to determine environment to rename\n\n"
            msg += textwrap.dedent("""
                Please re-run this command with one of the following options:

                * Provide an environment name via --name or -n
                OR
                * Provide an environment path via --prefix or -p
                * Re-run this command inside of an activated conda environment.""").lstrip()
            raise CondaEnvException(msg)
        if name:
            if os.sep in name:
                # assume "names" with a path seperator are actually paths
                args.prefix = name
            else:
                args.name = name
        else:
            args.prefix = prefix
    else:
        name = args.name
    prefix = get_prefix(args)
    env = from_environment(name, prefix, no_builds=args.no_builds,
                           ignore_channels=args.ignore_channels, from_history=args.from_history)

    # Commenting out the below code but keeping it around for reference in case it's useful
    # (from conda_env/cli/main_remove.py's execute() function)
    # args = vars(args)
    # args.update({
    #     'all': True, 'channel': None, 'features': None,
    #     'override_channels': None, 'use_local': None, 'use_cache': None,
    #     'offline': None, 'force': True, 'pinned': None})
    # args = Namespace(**args)
    # from conda.base.context import context
    # context.__init__(argparse_args=args)

    conda.cli.main_rename.execute(args, parser)


# conda_env/cli/main_create.py module's "execute" function is below (for reference):
# def execute(args, parser):
#     from conda.base.context import context
#     name = args.remote_definition or args.name
#
#     try:
#         spec = specs.detect(name=name, filename=get_filename(args.file), directory=os.getcwd())
#         env = spec.environment
#
#         # FIXME conda code currently requires args to have a name or prefix
#         # don't overwrite name if it's given. gh-254
#         if args.prefix is None and args.name is None:
#             args.name = env.name
#
#     except exceptions.SpecNotFound:
#         raise
#
#     prefix = get_prefix(args, search=False)
#
#     if args.force and prefix != context.root_prefix and os.path.exists(prefix):
#         rm_rf(prefix)
#     cli_install.check_prefix(prefix, json=args.json)
#
#     # TODO, add capability
#     # common.ensure_override_channels_requires_channel(args)
#     # channel_urls = args.channel or ()
#
#     result = {"conda": None, "pip": None}
#
#     args_packages = context.create_default_packages if not args.no_default_packages else []
#
#     if args.dry_run:
#         installer_type = 'conda'
#         installer = get_installer(installer_type)
#
#         pkg_specs = env.dependencies.get(installer_type, [])
#         pkg_specs.extend(args_packages)
#
#         solved_env = installer.dry_run(pkg_specs, args, env)
#         if args.json:
#             print(json.dumps(solved_env.to_dict(), indent=2))
#         else:
#             print(solved_env.to_yaml(), end='')
#
#     else:
#         if args_packages:
#             installer_type = "conda"
#             installer = get_installer(installer_type)
#             result[installer_type] = installer.install(prefix, args_packages, args, env)
#
#         if len(env.dependencies.items()) == 0:
#             installer_type = "conda"
#             pkg_specs = []
#             installer = get_installer(installer_type)
#             result[installer_type] = installer.install(prefix, pkg_specs, args, env)
#         else:
#             for installer_type, pkg_specs in env.dependencies.items():
#                 try:
#                     installer = get_installer(installer_type)
#                     result[installer_type] = installer.install(prefix, pkg_specs, args, env)
#                 except InvalidInstaller:
#                     sys.stderr.write(textwrap.dedent("""
#                         Unable to install package for {0}.
#
#                         Please double check and ensure your dependencies file has
#                         the correct spelling.  You might also try installing the
#                         conda-env-{0} package to see if provides the required
#                         installer.
#                         """).lstrip().format(installer_type)
#                     )
#                     return -1
#
#         if env.variables:
#             pd = PrefixData(prefix)
#             pd.set_environment_env_vars(env.variables)
#
#         touch_nonadmin(prefix)
#         print_result(args, prefix, result)


# &&&&&& Is this *actually* where clone happens?
# The below clone_env() function is copied from conda/misc.py for reference:
# def clone_env(prefix1, prefix2, verbose=True, quiet=False, index_args=None):
#     """
#     clone existing prefix1 into new prefix2
#     """
#     untracked_files = untracked(prefix1)
#
#     # Discard conda, conda-env and any package that depends on them
#     filter = {}
#     found = True
#     while found:
#         found = False
#         for prec in PrefixData(prefix1).iter_records():
#             name = prec['name']
#             if name in filter:
#                 continue
#             if name == 'conda':
#                 filter['conda'] = prec
#                 found = True
#                 break
#             if name == "conda-env":
#                 filter["conda-env"] = prec
#                 found = True
#                 break
#             for dep in prec.combined_depends:
#                 if MatchSpec(dep).name in filter:
#                     filter[name] = prec
#                     found = True
#
#     if filter:
#         if not quiet:
#             fh = sys.stderr if context.json else sys.stdout
#             print('The following packages cannot be cloned out of the root environment:', file=fh)
#             for prec in itervalues(filter):
#                 print(' - ' + prec.dist_str(), file=fh)
#         drecs = {prec for prec in PrefixData(prefix1).iter_records() if prec['name'] not in filter}
#     else:
#         drecs = {prec for prec in PrefixData(prefix1).iter_records()}
#
#     # Resolve URLs for packages that do not have URLs
#     index = {}
#     unknowns = [prec for prec in drecs if not prec.get('url')]
#     notfound = []
#     if unknowns:
#         index_args = index_args or {}
#         index = get_index(**index_args)
#
#         for prec in unknowns:
#             spec = MatchSpec(name=prec.name, version=prec.version, build=prec.build)
#             precs = tuple(prec for prec in itervalues(index) if spec.match(prec))
#             if not precs:
#                 notfound.append(spec)
#             elif len(precs) > 1:
#                 drecs.remove(prec)
#                 drecs.add(_get_best_prec_match(precs))
#             else:
#                 drecs.remove(prec)
#                 drecs.add(precs[0])
#     if notfound:
#         raise PackagesNotFoundError(notfound)
#
#     # Assemble the URL and channel list
#     urls = {}
#     for prec in drecs:
#         urls[prec] = prec['url']
#
#     precs = tuple(PrefixGraph(urls).graph)
#     urls = [urls[prec] for prec in precs]
#
#     disallowed = tuple(MatchSpec(s) for s in context.disallowed_packages)
#     for prec in precs:
#         if any(d.match(prec) for d in disallowed):
#             raise DisallowedPackageError(prec)
#
#     if verbose:
#         print('Packages: %d' % len(precs))
#         print('Files: %d' % len(untracked_files))
#
#     if context.dry_run:
#         raise DryRunExit()
#
#     for f in untracked_files:
#         src = join(prefix1, f)
#         dst = join(prefix2, f)
#         dst_dir = dirname(dst)
#         if islink(dst_dir) or isfile(dst_dir):
#             rm_rf(dst_dir)
#         if not isdir(dst_dir):
#             os.makedirs(dst_dir)
#         if islink(src):
#             symlink(readlink(src), dst)
#             continue
#
#         try:
#             with open(src, 'rb') as fi:
#                 data = fi.read()
#         except IOError:
#             continue
#
#         try:
#             s = data.decode('utf-8')
#             s = s.replace(prefix1, prefix2)
#             data = s.encode('utf-8')
#         except UnicodeDecodeError:  # data is binary
#             pass
#
#         with open(dst, 'wb') as fo:
#             fo.write(data)
#         shutil.copystat(src, dst)
#
#     actions = explicit(urls, prefix2, verbose=not quiet, index=index,
#                        force_extract=False, index_args=index_args)
#     return actions, untracked_files
