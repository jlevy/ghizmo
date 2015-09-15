"""
Common functions for commands.
"""

from __future__ import print_function

__author__ = 'jlevy'

# TODO: Move this module elsewhere?

import sys
import json


def status(message, dry_run=False):
  return {"message": message, "dry_run": dry_run}


def process_input(function):
  """
  Just for brevity, a generic handler to look up and process based on input.
  """
  for item in input_json_lines():
    yield function(item)


def input_json_lines():
  """
  Read line-delimited JSON stream.
  TODO: Handle jq-style streamed JSON that need not be line delimited.
  """
  for line in sys.stdin:
    yield json.loads(line)


def to_bool(str):
  if str in [True, "True", "true"]:
    return True
  elif str in [False, "False", "false"]:
    return False
  else:
    raise ValueError("Not a boolean: %r" % str)
