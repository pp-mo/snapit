import unittest as tests

import os
import os.path
import shutil

from snapit import snapshot

class TestSnapit(tests.TestCase):
    def test_snapit(self):
        # copy reference data to a new 'test data' directory.
        ref_path = './data_testing/ref_data'
        tgt_path = './data_testing/test_data'
        if os.path.exists(tgt_path):
            shutil.rmtree(tgt_path)
        shutil.copytree(ref_path, tgt_path, symlinks=True)
        current_path = os.path.join(tgt_path, 'current')

        # Snapshot the test data.
        snapshot(current_path, snapshot_name='snapshot_2')

        # Perform various checks on the results.
        def check_path(relpath, isfile=False, isdir=False, link=None):
            path = os.path.join(tgt_path, relpath)
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


# Test the result.
if __name__ == '__main__':
    tests.main()
