"""
Pre-defined commands.

Public functions here (not starting with '_') are auto-registered into Ghizmo's command line.

For GitHub the library API, see: https://github.com/sigmavirus24/github3.py
"""

from __future__ import print_function

import logging as log

from command_lib import read_json_lines


def tags(config, args):
  """
  All tag info.
  """
  repo = config.repo
  formatter = config.formatter
  for tag in repo.tags():
    formatter(tag)


def branches(config, args):
  """
  All branch info.
  """
  repo = config.repo
  formatter = config.formatter
  for branch in repo.branches():
    formatter(branch)


def refs(config, args):
  """
  All ref info.
  """
  repo = config.repo
  formatter = config.formatter
  for ref in repo.refs():
    formatter(ref)


def _delete_ref(repo, ref_name, force, dry_run):
  ref = repo.ref(ref_name)
  if not ref and not force:
    raise ValueError("Reference not found: %s" % ref_name)
  log.warn("Delete reference: %s", ref_name)
  if not dry_run:
    ref.delete()


def delete_refs(config, args):
  """
  Delete references by name.
  """
  repo = config.repo
  force = args.force
  dry_run = args.dry_run
  for ref_name in read_json_lines():
    _delete_ref(repo, ref_name, force, dry_run)


def delete_branches(config, args):
  """
  Delete branches by name.
  """
  repo = config.repo
  force = args.force
  dry_run = args.dry_run
  for ref_name in read_json_lines():
    _delete_ref(repo, "heads/" + ref_name, force, dry_run)


def pull_requests(config, args):
  """
  All PR info.
  """
  repo = config.repo
  formatter = config.formatter
  state = args.state or "open"
  for pr in repo.pull_requests(state=state):
    formatter(pr)


def contributors(config, args):
  """
  Contributor info.
  """
  repo = config.repo
  formatter = config.formatter
  for c in repo.contributors():
    formatter(c)


def stale_pr_branches(config, args):
  """
  List "stale" branches that associated with a closed PR and are from the same
  (non-forked) repository as the base.
  """
  repo = config.repo
  formatter = config.formatter
  repo_url = repo.url
  for pr in repo.pull_requests(state="closed"):
    is_stale = False
    if pr.head.repo == pr.base.repo:
      branch = repo.branch(pr.head.ref)
      if branch:
        is_stale = True
    if is_stale:
      formatter({"html_url": pr.html_url,
                 "base_branch": pr.base.ref,
                 "head_branch": pr.head.ref,
                 })
