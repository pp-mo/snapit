#!/bin/env python2.7
#
# Plot timing data from output of "run_benchmarks.py", in:
#   https://gitlab.com/pelson/performance-metrics/blob/master/
#
# Currently works with sample test result (included in this repo for now).
#
from __future__ import division

import datetime
import six
import shutil
import os
import os.path


DEFAULT_CURRENT_PATH = './current/'
TIMESTAMP_STRFTIME_FMT = '%Y-%m-%d_%H:%M:%S'
INFO_VERBOSE = False
INFO_DRYRUN = False

def info(message):
    if INFO_VERBOSE:
        if INFO_DRYRUN:
            message = 'Would: ' + message
        print(message)


def ensure_path(path):
    if not os.path.exists(path):
        os.makedirs(path)


def make_soft_image(target_dirpath, relative_source_dirpath, dryrun=False):
    """
    Create a duplicate of a directory with relative-path softlinks for all
    content.

    Sub-directories in the source produce new actual sub-directories in the
    target, which are soft images of the source sub-dirs.

    Args:
    * target_dirpath (string):
        path to the target output dir.
        If it does not already exist it will be created.
        If it does already exist, it must be empty.
    * relative_source_dirpath (string):
        directory to create an image of, as a path relative to the target.
    * dryrun (bool):
        don't actually perform (N.B. debug output is controlled by globals).

    """
    actual_source_dirpath = os.path.join(target_dirpath,
                                         relative_source_dirpath)
    info('Make soft image of {!r} in {!r}'.format(
        actual_source_dirpath, target_dirpath))

    # Create target if it does not exist.
    info('Ensure {!r} exists.'.format(target_dirpath))
    if not dryrun:
        ensure_path(target_dirpath)

    # Check target is empty.
    info('Check {!r} is empty.'.format(target_dirpath))
    if len(os.listdir(target_dirpath)) > 0:
        msg = 'Aborted creating links in "{!s}" as it is not empty.'
        raise ValueError(msg.format(target_dirpath))

    # Fill target with pointers to the source data.
    for name in os.listdir(actual_source_dirpath):
        info('Create soft-link for {!r} in {!r}'.format(
            name, actual_source_dirpath))
        target_path = os.path.join(target_dirpath, name)
        source_relative_path = os.path.join(relative_source_dirpath, name)
        source_actual_path = os.path.join(target_dirpath, source_relative_path)
        if os.path.isdir(source_actual_path):
            # Recurse to create sub-directory.
            # Make path to the source subdir relative to the target subdir.
            source_subdir_relative_path = os.path.join(
                '..', source_relative_path)
            make_soft_image(target_path, source_subdir_relative_path,
                            dryrun=dryrun)
        else:
            # Create a softlink.
            if os.path.islink(source_actual_path):
                # Don't link to a link -- copy it instead.
                # NOTE: this only works because snapshots share a structure
                # and all softlinks go through the parent directory.
                # So a relative path like "../../snap_1/subdir_a/actual_file"
                # is correct from within *any* "<snapshot>/subdir_a".
                source_relative_path = os.readlink(source_actual_path)
            info('Create softlink at {!r} to {!r}.'.format(
                target_path, source_relative_path))
            if not dryrun:
                os.symlink(source_relative_path, target_path)


def snapshot(current_path=None,
             snapshot_name=None,
             verbose=False, dryrun=False):
    """
    Snapshot the contents of a directory tree using softlinks.

    The existing directory is renamed as a snapshot within the same parent
    directory, and it is replaced by a new current-state directory of the same
    name, containing softlinks to all the old content.

    Any existing softlinks within the tree should contain relative paths routed
    through the common parent directory.  The softlinks created by the snapshot
    process conform to this.

    Args:
    * current_path (string):
        path to the existing 'current' directory to be snapshotted + replaced.
    * snapshot_name (string):
        filename for the new snapshot.  Defaults to a timestamp.
    * dryrun (bool):
        show what would happen, but do not act.  Implies 'verbose'.
    * verbose (bool):
        print summary of actions. Defaults to ='dryrun'.

    """
    if verbose is None:
        verbose = dryrun

    if not os.path.exists(current_path):
        msg = 'Current content path, "{!s}", does not exist.'
        raise ValueError(msg.format(current_path))

    parent_path = os.path.dirname(current_path)

    # The snapshot name defaults to a timestamp.
    if snapshot_name is None:
        timestamp = datetime.datetime.now()
        snapshot_name = timestamp.strftime(TIMESTAMP_STRFTIME_FMT)
    snapshot_path = os.path.join(parent_path, snapshot_name)

    # Rename the current content to the snapshot path.
    info('Move (rename) target {!r} to new snapshot {!r}'.format(
        current_path, snapshot_path))
    if not dryrun:
        shutil.move(current_path, snapshot_path)

    # Create a new 'current' full of links to the original content.
    snapshot_relative_path = os.sep.join(['..', snapshot_name])
    make_soft_image(current_path, snapshot_relative_path, dryrun=dryrun)


def _make_parser():
    import argparse
    parser = argparse.ArgumentParser(
        description='Snapshot a directory.')
    parser.add_argument('--current', '-c', type=str, default=None,
                        help=('Directory with current contents to snapshot '
                              '[default = {}].').format(
                                  DEFAULT_CURRENT_PATH))
    parser.add_argument('--name', '-n', type=str, default=None,
                        help=('Name for snapshot [default = a timestamp].'))
#    parser.add_argument('--comment', '-c', type=str,
#                        help=('Create snapshot comment file.'))
#    parser.add_argument('--comment-filename', '-n', type=str,
#                        default='snapshot.file',
#                        help=('Create snapshot comment file.'))
#    parser.add_argument('--verbose', '-v', action="store_true",
#                        help=('Print details.'))
#    parser.add_argument('--dry-run', action="store_true",
#                        help=('Do nothing, but show what would happen.'))
    return parser


if __name__ == '__main__':
    parser = _make_parser()
    args = parser.parse_args()

    INFO_VERBOSE = args.verbose or args.dryrun
    INFO_DRYRUN = args.dryrun

    snapshot(current_path=args.current,
             snapshot_name=args.name)
