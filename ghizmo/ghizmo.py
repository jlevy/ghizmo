"""
Ghizmo main library.
"""

from __future__ import print_function

__author__ = 'jlevy'

import logging as log
import sys
import json
import yaml
import inspect
import getpass
from collections import namedtuple
from functools32 import lru_cache  # functools32 pip
import github3  # github3.py pip
from github3.null import NullObject

import configs
import commands


def read_login_info(username=None):
  if not username:
    username = raw_input("GitHub username: ")
  return (username, getpass.getpass())


def login(username=None):
  token = configs.get_access_token()
  if token:
    log.info("Using access token authentication")
    return github3.login(token=token)
  else:
    username = username or configs.get_username()
    return github3.login(*read_login_info(username=username))


def format_to_string(obj, format=None):
  if not format:
    format = "json"

  if isinstance(obj, NullObject):
    raise ValueError("Command returned null type (invalid input?): %s" % repr(obj))

  # Heuristic to convert github3 objects to serializable form.
  if hasattr(obj, "as_dict"):
    obj = obj.as_dict()

  if format == "json":
    return json.dumps(obj, sort_keys=True, indent=2) + "\n"
  elif format == "yaml":
    return yaml.safe_dump(obj, default_style='"')
  else:
    raise AssertionError("Invalid format: %s" % format)


def print_formatter(format=None):
  def printer(obj):
    print(format_to_string(obj, format), end="")
    sys.stdout.flush()

  return printer

# The configuration to run.
Config = namedtuple("Config", "repo formatter")


def _to_dash(name):
  return name.replace("_", "-")


def _to_underscore(name):
  return name.replace("-", "_")


def all_command_functions():
  def is_public_func(f):
    return inspect.isfunction(f) and not f.__name__.startswith("_")

  return inspect.getmembers(commands, predicate=is_public_func)


@lru_cache()
def command_directory(use_dashes=True):
  def doc_for_function(func):
    if func.__doc__:
      return func.__doc__.strip()
    else:
      return "(no pydoc)"

  transform = _to_dash if use_dashes else lambda x: x
  return [(transform(name), doc_for_function(func)) for (name, func) in all_command_functions()]


@lru_cache()
def list_commands(use_dashes=True):
  return [command for (command, doc) in command_directory(use_dashes=use_dashes)]


def get_command_func(command):
  command = _to_underscore(command)
  if not command in list_commands(use_dashes=False):
    raise ValueError("invalid command: %s" % command)
  return getattr(commands, command)


def run_command(command, config, args):
  command_func = get_command_func(command)
  log.info("Command '%s' (%s)", command, command_func)
  log.info("Config: %s", config)
  log.info("Args: %s", args)
  # This executes the command step by step, either just to display results, or to display progress
  # on an action with side effects.
  for result in command_func(config, args):
    config.formatter(result)

# TODO:
# Automagic loading of ghizmo_commands.py files from current directory.
# Proper streaming of JSON items (as opposed to line-by-line), for use in piping.
# Prettier SIGPIPE handling
