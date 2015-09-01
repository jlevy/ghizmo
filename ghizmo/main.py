#!/usr/bin/env python
"""
For further documentation, see: https://github.com/jlevy/ghizmo
"""

from __future__ import print_function

__author__ = 'jlevy'

import logging as log
import sys
import argparse

NAME = "ghizmo"
VERSION = "0.1.1"
DESCRIPTION = "ghizmo: Extensible GitHub command-line tricks"
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


def main():
  import ghizmo
  import configs

  parser = argparse.ArgumentParser(description=DESCRIPTION, version=VERSION, epilog="\n" + __doc__,
                                   formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("command", help="%s command" % NAME, choices=ghizmo.list_commands(use_dashes=True))
  parser.add_argument("--state", help="pull requests state", choices=["open", "closed", "all"])
  parser.add_argument("--format", help="output format", choices=["json", "yaml"])
  parser.add_argument("--username", help="username to log in as")
  parser.add_argument("--repo", help="repo of the form: owner/repo-name")
  parser.add_argument("-f", "--force", help="enable debugging output", action="store_true")
  parser.add_argument("-n", "--dry-run", help="dry run: log actions but don't do anything", action="store_true")
  parser.add_argument("--debug", help="enable debugging output", action="store_true")
  args = parser.parse_args()

  log_setup(log.DEBUG if args.debug else log.WARN)

  # Validate credentials and log in.
  gh = ghizmo.login(username=args.username)
  if not gh:
    raise ValueError("Login failure")

  # Validate repository.
  if args.repo:
    (owner, repo_name) = args.repo.split("/")
  else:
    (owner, repo_name) = configs.infer_repo()
  repo = gh.repository(owner, repo_name)
  if not repo:
    raise ValueError("Couldn't access repository: %s/%s" % (owner, repo_name))

  # Assemble config for this run.
  formatter = ghizmo.print_formatter(args.format)
  config = ghizmo.Config(repo=repo, formatter=formatter, dry_run=args.dry_run)

  ghizmo.run_command(args.command, config, args)


if __name__ == '__main__':
  main()
