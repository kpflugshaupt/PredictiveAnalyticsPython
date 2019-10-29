# make imports from pa_lib possible (parent directory of file's directory)
import sys
from pathlib import Path

_file_dir = Path.cwd()
_parent_dir = _file_dir.parent
sys.path.append(str(_parent_dir))

# Imports
from pa_lib.job import request_job

request_job("jobtest_2")
request_job("jobtest_3")

print("Hello from jobtest_1!")

sys.exit()
