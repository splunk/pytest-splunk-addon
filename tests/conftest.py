import copy
import shutil
from textwrap import dedent

import pytest
import six

try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib

pytest_plugins = "pytester"

REPOSITORY_ROOT = pathlib.Path(__file__).parent