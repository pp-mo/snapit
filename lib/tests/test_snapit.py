import os
import os.path
import shutil

from snapit import snapshot

REF_PATH = './data_testing/ref_data'
TGT_PATH = './data_testing/test_data'
if os.path.exists(TGT_PATH):
    shutil.rmtree(TGT_PATH)
shutil.copytree(REF_PATH, TGT_PATH, symlinks=True)

CURRENT_PATH = os.path.join(TGT_PATH, 'current')
snapshot(CURRENT_PATH, snapshot_name='snapshot_2')