#
# Take a "snapshot" of a directory.
#
# The directory is renamed as a snapshot, and replaced by a copy containing
# softlinks to all the content.
#
import datetime
import six
import shutil
import os
import os.path


DEFAULT_CURRENT_PATH = './current/'
TIMESTAMP_STRFTIME_FMT = '%Y-%m-%d_%H:%M:%S'
INFO_VERBOSE = False
INFO_DRYRUN = False


def _log_message(message):
    print(message)


def _info(message):
    if INFO_VERBOSE:
        if INFO_DRYRUN:
            message = 'Would: ' + message
        _log_message(message)


def _ensure_path(path):
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
    _info('[Make soft image of {!r} in {!r}]'.format(
        actual_source_dirpath, target_dirpath))

    # Create target if it does not exist.
    _info('Ensure {!r} exists.'.format(target_dirpath))
    if not dryrun:
        _ensure_path(target_dirpath)

    # Check target is empty.
    _info('Check {!r} is empty.'.format(target_dirpath))
    if not dryrun and len(os.listdir(target_dirpath)) > 0:
        msg = 'Aborted creating links in "{!s}" as it is not empty.'
        raise ValueError(msg.format(target_dirpath))

    # Fill target with pointers to the source data.
    listing_path = target_dirpath if dryrun else actual_source_dirpath
    for name in os.listdir(listing_path):
        target_path = os.path.join(target_dirpath, name)
        _info('[[Make link for {!r} ...]]'.format(target_path))
        source_relative_path = os.path.join(relative_source_dirpath, name)
        if dryrun:
            source_actual_path = target_path
        else:
            source_actual_path = os.path.join(actual_source_dirpath,
                                              source_relative_path)
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
            _info('Create softlink at {!r} to {!r}.'.format(
                target_path, source_relative_path))
            if not dryrun:
                os.symlink(source_relative_path, target_path)


def snapshot(current_path,
             snapshot_name=None,
             verbose=None, dryrun=False):
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
        The new snapshot will be created in its parent directory.
    * snapshot_name (string):
        filename for the new snapshot.  Defaults to a timestamp.
    * dryrun (bool):
        show what would happen, but do not act.  Implies 'verbose'.
    * verbose (bool):
        print summary of actions. Defaults to ='dryrun'.

    """
    if verbose is None:
        verbose = dryrun

    global INFO_DRYRUN, INFO_VERBOSE
    INFO_DRYRUN, INFO_VERBOSE = dryrun, verbose

    if not os.path.exists(current_path):
        msg = 'Current content path, "{!s}", does not exist.'
        raise ValueError(msg.format(current_path))

    parent_path = os.path.dirname(current_path)

    # The snapshot name defaults to a timestamp.
    if snapshot_name is None:
        timestamp = datetime.datetime.now()
        timestamp = timestamp.strftime(TIMESTAMP_STRFTIME_FMT)
        key_name = os.path.basename(current_path)
        snapshot_name = 'snapshot_{}_{}'.format(key_name, timestamp)
    snapshot_path = os.path.join(parent_path, snapshot_name)

    # Rename the current content to the snapshot path.
    _info('Move (rename) target {!r} to new snapshot {!r}'.format(
        current_path, snapshot_path))
    if not dryrun:
        shutil.move(current_path, snapshot_path)

    # Create a new 'current' full of links to the original content.
    snapshot_relative_path = os.sep.join(['..', snapshot_name])
    make_soft_image(current_path, snapshot_relative_path, dryrun=dryrun)
