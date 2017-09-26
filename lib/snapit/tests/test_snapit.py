import unittest as tests

import mock
import os
import os.path
import re
import shutil

import snapit
from snapit import snapshot


class TestSnapit(tests.TestCase):
    def setUp(self):
        # copy reference data to a new 'test data' directory.
        snapit_path = os.path.dirname(snapit.__file__)
        data_testing_path = os.path.join(snapit_path, 'tests/data_testing')
        self.ref_path = os.path.join(data_testing_path, 'ref_data')
        self.tgt_path = os.path.join(data_testing_path, 'test_data')
        if os.path.exists(self.tgt_path):
            shutil.rmtree(self.tgt_path)
        shutil.copytree(self.ref_path, self.tgt_path, symlinks=True)
        self.current_path = os.path.join(self.tgt_path, 'current')

    def check_path(self, relpath, isfile=False, isdir=False, link=None):
        # Check the form of a specific target path.
        path = os.path.join(self.tgt_path, relpath)
        self.assertTrue(os.path.exists(path))
        if isfile:
            self.assertTrue(os.path.isfile(path))
        elif isdir:
            self.assertTrue(os.path.isdir(path))
        else:
            self.assertTrue(os.path.islink(path))
            self.assertEqual(os.readlink(path), link)

    def test_simple(self):
        # Snapshot the test data.
        snapshot(self.current_path, snapshot_name='snapshot_2')

        # Perform various checks on the results.
        self.check_path('current/file_1.txt', link='../snapshot_2/file_1.txt')
        self.check_path('current/subdir', isdir=True)
        self.check_path('current/subdir/file_2.txt',
                        link='../../snapshot_1/subdir/file_2.txt')
        self.check_path('current/subdir/extra_file_2_2.txt',
                        link='../../snapshot_2/subdir/extra_file_2_2.txt')

        self.check_path('snapshot_2/file_1.txt', isfile=True)
        self.check_path('snapshot_2/subdir/file_2.txt',
                        link='../../snapshot_1/subdir/file_2.txt')
        self.check_path('snapshot_2/subdir/extra_file_2_2.txt', isfile=True)

        self.check_path('snapshot_1/file_1.txt', isfile=True)
        self.check_path('snapshot_1/subdir/file_2.txt', isfile=True)

    def check_output(self, dryrun=False, verbose=False):
        # Check messages for the standard test run with dryrun or verbose.
        with mock.patch('snapit._log_message') as patch_info:
            snapshot(self.current_path, snapshot_name='snapshot_2',
                     dryrun=dryrun, verbose=verbose)

            call_args = patch_info.call_args_list

            woulds = [arg[0][0].startswith('Would: ') for arg in call_args]
            if dryrun:
                self.assertTrue(all(woulds))
            else:
                self.assertTrue(all([not would for would in woulds]))

            patt = (r".*\[Make soft image of .*current/\.\./snapshot_2' "
                    r"in '.*current'\]")
            self.assertTrue(re.match(patt, call_args[1][0][0]))

            patt = (r".*Create softlink at '.*current/file_1\.txt' "
                    r"to '\.\./snapshot_2/file_1\.txt'")
            self.assertTrue(re.match(patt, call_args[5][0][0]))

            patt = (r".*\[Make soft image of "
                    r"'.*current/subdir/\.\./\.\./snapshot_2/subdir' "
                    r"in '.*current/subdir'\]")
            self.assertTrue(re.match(patt, call_args[7][0][0]))

    def test_dryrun(self):
        self.check_output(dryrun=True, verbose=True)
        self.assertFalse(os.path.exists(self.tgt_path + '/snapshot_2'))

    def test_verbose(self):
        self.check_output(verbose=True)
        self.assertTrue(os.path.exists(self.tgt_path + '/snapshot_2'))


# Test the result.
if __name__ == '__main__':
    tests.main()
