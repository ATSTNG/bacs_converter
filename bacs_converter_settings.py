import datetime
from pathlib import Path

# conversion settings
NAME_PREFIX = ''
NAME_SUFFIX = ''
MAIN_LANG = 'russian'
MAINTAINERS_LIST = ['ATSTNG']

# script settings
# (not recommended to change unless you know what you're doing)
ROOT = Path(__file__).resolve().parent
TASK_BACS_EXAMPLE = ROOT / "_example_bacs_task"
BACS_CONVERTER_REVISION = datetime.datetime(2025, 10, 19)

DEBUG_SKIP_PROBLEM_PACKAGE_DO_ALL = False

