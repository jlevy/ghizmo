"""
Ghizmo main library.
"""

from __future__ import print_function

__author__ = 'jlevy'

import logging as log
import sys
import re
import json
import yaml
import inspect
import os
import importlib
import getpass
from collections import namedtuple
from collections import OrderedDict
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


# All data used by the run of a command.
Config = namedtuple("Config", "github repo formatter")


def _to_dash(name):
  return name.replace("_", "-")


def _to_underscore(name):
  return name.replace("-", "_")


def _is_public_func(f):
  return inspect.isfunction(f) and not f.__name__.startswith("_")


@lru_cache()
def all_command_functions():
  # TODO: Clean this up somehow.
  # Use absolute module path so it works post installation.
  modules = [importlib.import_module("ghizmo.commands.%s" % module) for module in commands.__all__]

  # If there is a ghizmo_commands.py file in the current directory, use it too.
  if os.path.exists("ghizmo_commands.py"):
    sys.path.insert(1, '.')  # This is needed only on some installations.
    modules.append(importlib.import_module("ghizmo_commands"))

  log.info("Imported command modules: %s", modules)

  func_map = {}
  for module in modules:
    for (name, func) in inspect.getmembers(module, predicate=_is_public_func):
      if name in func_map:
        raise ValueError("Duplicate function name for command: %s" % name)
      func_map[name] = func
  # Sort items first by module, then by name.
  return OrderedDict(sorted(func_map.items(), key=lambda (name, func): (func.__module__, name)))


@lru_cache()
def command_directory(use_dashes=True):
  def doc_for_function(func):
    doc = func.__doc__ and re.sub("\s+", " ", func.__doc__).strip()
    if not doc:
      doc = "(no pydoc)"
    return doc

  transform = _to_dash if use_dashes else lambda x: x
  return [(func.__module__, transform(name), doc_for_function(func)) for (name, func) in
          all_command_functions().iteritems()]


@lru_cache()
def list_commands(use_dashes=True):
  return [command for (module, command, doc) in command_directory(use_dashes=use_dashes)]


def get_command_func(command):
  command = _to_underscore(command)
  if not command in all_command_functions():
    raise ValueError("invalid command: %s" % command)
  return all_command_functions()[command]


def run_command(command, config, args):
  command_func = get_command_func(command)
  log.info("Command '%s' (%s)", command, command_func)
  log.info("Config: %s", config)
  log.info("Args: %s", args)
  # This executes the command step by step, either just to display results, or to display progress
  # on an action with side effects.
  iterable_result = command_func(config, args)
  if iterable_result:
    for result in iterable_result:
      config.formatter(result)

# TODO:
# Control pretty-printing, using one object per line by default, but with --pretty option to print nicely
# Proper reading of JSON streams (as opposed to line-by-line), for use in piping
# Prettier SIGPIPE handling
