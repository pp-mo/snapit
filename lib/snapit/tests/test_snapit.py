import unittest as tests

import os
import os.path
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

    def test_snapit(self):
        # Snapshot the test data.
        snapshot(self.current_path, snapshot_name='snapshot_2')

        # Perform various checks on the results.
        def check_path(relpath, isfile=False, isdir=False, link=None):
            path = os.path.join(self.tgt_path, relpath)
            self.assertTrue(os.path.exists(path))
            if isfile:
                self.assertTrue(os.path.isfile(path))
            elif isdir:
                self.assertTrue(os.path.isdir(path))
            else:
                self.assertTrue(os.path.islink(path))
                self.assertEqual(os.readlink(path), link)

        check_path('current/file_1.txt', link='../snapshot_2/file_1.txt')
        check_path('current/subdir', isdir=True)
        check_path('current/subdir/file_2.txt',
                   link='../../snapshot_1/subdir/file_2.txt')
        check_path('current/subdir/extra_file_2_2.txt',
                   link='../../snapshot_2/subdir/extra_file_2_2.txt')

        check_path('snapshot_2/file_1.txt', isfile=True)
        check_path('snapshot_2/subdir/file_2.txt',
                   link='../../snapshot_1/subdir/file_2.txt')
        check_path('snapshot_2/subdir/extra_file_2_2.txt', isfile=True)

        check_path('snapshot_1/file_1.txt', isfile=True)
        check_path('snapshot_1/subdir/file_2.txt', isfile=True)

    def test_dryrun(self):
        snapshot(self.current_path, dryrun=True)


# Test the result.
if __name__ == '__main__':
    tests.main()
