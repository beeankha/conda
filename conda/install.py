import os
import tarfile
import logging
from os.path import join

from sfx import yield_lines, sfx_activate


log = logging.getLogger(__name__)

# Note: in the functions below the following argument names refer to:
#
#     pkg:         canonical package name (e.g. 'numpy-1.6.2-py26_0')
#
#     pkgs_dir:    the "packages directory" (e.g. '/opt/anaconda/pkgs')
#
#     env_prefix:  the prefix of a particular environment, which may also
#                  be the "default" environment (i.e. '/opt/anaconda'),
#                  but is otherwise something like '/opt/anaconda/envs/foo',
#                  or even any prefix, e.g. '/home/joe/myenv'

def extract(pkgs_dir, pkg, cleanup=False):
    '''
    extract a package tarball into the conda packages directory, making
    it available
    '''
    dirpath = join(pkgs_dir, pkg)
    bz2path = join(pkgs_dir, pkg + '.tar.bz2')
    t = tarfile.open(bz2path)
    t.extractall(path=dirpath)
    t.close()
    if cleanup:
        os.unlink(bz2path)


def activate(pkgs_dir, pkg, env_prefix):
    '''
    set up link farm for the specified package, in the specified conda
    environment
    '''
    sfx_activate(pkgs_dir, pkg, env_prefix)


def deactivate(pkgs_dir, pkg, env_prefix):
    '''
    tear down link farm for the specified package, in the specified
    Anaconda environment
    '''
    dist_path = join(pkgs_dir, pkg)
    dst_dirs = set()
    for f in yield_lines(join(dist_path, 'info/files')):
        fdn, fbn = os.path.split(f)
        dst_dir = join(env_prefix, fdn)
        dst_dirs.add(dst_dir)
        dst = join(dst_dir, fbn)
        try:
            os.unlink(dst)
        except OSError: # file might not exist
            log.debug("could not remove file: '%s'" % dst)

    for path in sorted(dst_dirs, key=len, reverse=True):
        try:
            os.rmdir(path)
        except OSError: # directory might not exist or not be empty
            log.debug("could not remove directory: '%s'" % dst)

