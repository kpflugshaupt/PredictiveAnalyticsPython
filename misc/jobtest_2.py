# make imports from pa_lib possible (parent directory of file's directory)
import sys
from pathlib import Path

_file_dir = Path.cwd()
_parent_dir = _file_dir.parent
sys.path.append(str(_parent_dir))

# Imports
from pa_lib.job import request_job
from pa_lib.log import info

info(f"Starting jobtest_2.py")
request_job("jobtest_4.py", current="Today")

info("Ending jobtest_2.py!")
