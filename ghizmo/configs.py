"""
Ghizmo config handling.
"""

from __future__ import print_function

__author__ = 'jlevy'

import logging as log
import os
import re
import yaml
import subprocess

from functools32 import lru_cache  # functools32 pip

CONFIG_FILENAME = ".ghizmo.yml"


@lru_cache()
def load_config_file():
  path = os.path.join(os.environ["HOME"], CONFIG_FILENAME)

  parsed_configs = None
  if os.path.exists(path):
    with open(path) as f:
      parsed_configs = yaml.safe_load(f)

  return parsed_configs


def get_username():
  configs = load_config_file()
  return configs and configs["username"]


def get_access_token():
  """Return GitHub auth token, if in config file."""
  configs = load_config_file()
  return configs and configs["access_token"]


def _extract_github_repo_info(url):
  m = re.match("^git@github.com:([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+).git$", url) or \
      re.match("^https://github.com/([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+).git$", url)
  return (m.group(1), m.group(2)) if m else None


def infer_repo(remote_name="origin"):
  """
  Extract the current repository info, if available, using .git/config in current working directory.
  """
  log.info("Checking in cwd for git dirctory: %s", os.getcwd())
  remote_url = subprocess.check_output(["git", "config", "--get", "remote.%s.url" % remote_name])
  (owner, repo_name) = _extract_github_repo_info(remote_url)
  log.info("Inferred repository: %s/%s", owner, repo_name)
  return (owner, repo_name)
