import os
import sys
sys.path.insert(0, os.path.abspath('../pytest_splunk_addon'))
extensions = ['sphinx.ext.napoleon']
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

import sphinx_rtd_theme
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']