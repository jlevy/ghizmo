"""
Common functions for commands.
"""

from __future__ import print_function

__author__ = 'jlevy'

import sys
import json


def read_json_lines():
  """
  Read line-delimited JSON stream.
  """
  for line in sys.stdin:
    yield json.loads(line)
