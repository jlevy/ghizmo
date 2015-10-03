#!/usr/bin/env python
"""
If commands require input, it must be line-delimited JSON (e.g. quoted strings).

For further documentation, see: https://github.com/jlevy/ghizmo
"""

from __future__ import print_function

__author__ = 'jlevy'

import logging as log
import sys
import os
import argparse
from commands.lib import to_bool

NAME = "ghizmo"
VERSION = "0.1.9"
DESCRIPTION = "ghizmo: An extensible command line for GitHub"
LONG_DESCRIPTION = __doc__


def log_setup(level):
  if level == log.DEBUG:
    log.basicConfig(format="%(levelname).1s %(filename)20s:%(lineno)-4d  %(message)s", level=level,
                    stream=sys.stderr)
  else:
    log.basicConfig(format="%(message)s", level=level, stream=sys.stderr)

    def brief_excepthook(exctype, value, traceback):
      print("error: %s" % value, file=sys.stderr)
      print("(run with --debug for traceback info)", file=sys.stderr)
      sys.exit(2)

    sys.excepthook = brief_excepthook


class UserArgs(object):
  """
  Assembles user-supplied arguments plus environment vars for convenient access.
  """

  def __init__(self):
    self._explicit_keys = []
    self.dict = {}

  def add_explicit(self, d):
    self.dict.update(d)
    self._explicit_keys.extend(d.keys())

  def add_implicit(self, d):
    self.dict.update(d)

  def get(self, item, default=None):
    return self.dict[item] if item in self.dict else default

  def get_bool(self, item, default=False):
    return to_bool(self.get(item, default))

  def __getattr__(self, item):
    try:
      return self.dict[item]
    except KeyError:
      raise AttributeError("Missing user-supplied argument '%s' (set with: --arg %s=VALUE)" % (item, item))

  def __str__(self):
    return ", ".join(["%s=%s" % (key, self.dict[key]) for key in self._explicit_keys])


def assemble_args(cmdline_args):
  assembled = UserArgs()

  user_arg_list = cmdline_args.arg or []
  d = {}
  for arg in user_arg_list:
    try:
      (key, value) = arg.split("=", 1)
    except:
      raise ValueError("Could not parse argument -- invalid format: '%s'" % arg)
    d[key] = value

  # Arguments are explicit, from command line, and from environment.
  assembled.add_implicit(os.environ)
  assembled.add_explicit(d)
  assembled.add_explicit({
    "dry_run": cmdline_args.dry_run,
    "force": cmdline_args.force,
    "format": cmdline_args.format
  })

  return assembled


def main():
  # Bootstrap logging right up front, so we do it before assembling commands for help.
  log_setup(log.DEBUG if "--debug" in sys.argv else log.WARN)

  import ghizmo
  import configs

  command_directory = ghizmo.command_directory()
  command_modules = sorted(set([module for (module, name, doc) in command_directory]))
  command_docs = \
    "command modules: %s\n" % ", ".join(command_modules) \
    + "(augment by adding to ./ghizmo_commands.py)\n\n" \
    + "commands available:\n" \
    + "\n".join(["  %s: %s" % (name, doc) for (module, name, doc) in command_directory])
  parser = argparse.ArgumentParser(description=DESCRIPTION, version=VERSION,
                                   epilog="\n" + __doc__ + "\n" + command_docs,
                                   formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("command", help="%s command" % NAME, choices=ghizmo.list_commands())
  parser.add_argument("--username", help="username to log in as")
  parser.add_argument("--repo", help="repo of the form: owner/repo-name")
  parser.add_argument("--debug", help="enable debugging output", action="store_true")

  # Command arguments:
  parser.add_argument("-f", "--force", help="enable debugging output", action="store_true")
  parser.add_argument("-n", "--dry-run", help="dry run: log actions but don't do anything", action="store_true")
  parser.add_argument("--format", help="output format", choices=["json", "yaml"])
  parser.add_argument("-a", "--arg", help="argument of the form key=value (may repeat this)", action="append")

  args = parser.parse_args()

  # Validate credentials and log in.
  gh = ghizmo.login(username=args.username)
  if not gh:
    raise ValueError("Login failure")

  # Validate repository.
  owner = None
  repo_name = None
  if args.repo:
    try:
      (owner, repo_name) = args.repo.split("/")
    except:
      raise ValueError("Invalid repository (use format owner/repo-name): %s" % args.repo)
  else:
    try:
      (owner, repo_name) = configs.infer_repo()
    except:
      log.debug("couldn't infer repository", exc_info=True)

  repo = None
  if owner and repo_name:
    repo = gh.repository(owner, repo_name)
    if not repo:
      raise ValueError("Couldn't access repository: %s/%s" % (owner, repo_name))

  # Assemble config for this run.
  formatter = ghizmo.print_formatter(args.format)
  config = ghizmo.Config(github=gh, repo=repo, formatter=formatter)

  ghizmo.run_command(args.command, config, assemble_args(args))


if __name__ == '__main__':
  main()
