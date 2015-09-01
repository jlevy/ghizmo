"""
Pre-defined commands.

Public functions here (not starting with '_') are auto-registered into Ghizmo's command line.

For GitHub the library API, see: https://github.com/sigmavirus24/github3.py
"""

from __future__ import print_function

import logging as log
import command_lib as lib


def tags(config, args):
  """
  List all tags.
  """
  return config.repo.tags()


def show_tags(config, args):
  """
  Show info for tags supplied on stdin.
  """
  for item in lib.input_json_lines():
    yield config.repo.tag(item)


def _delete_ref(repo, ref_name, force, dry_run):
  ref = repo.ref(ref_name)
  if not ref and not force:
    raise ValueError("Reference not found: %s" % ref_name)
  if not dry_run:
    ref.delete()
  return lib.status("Deleted %s" % ref_name, dry_run=dry_run)


def branches(config, args):
  """
  List all branches.
  """
  return config.repo.branches()


def show_branches(config, args):
  """
  Show branches supplied on stdin.
  """
  for item in lib.input_json_lines():
    yield config.repo.branch(item)


def delete_branches(config, args):
  """
  Delete branches supplied on stdin.
  """
  for ref_name in lib.input_json_lines():
    yield _delete_ref(config.repo, "heads/" + ref_name, args.force, args.dry_run)


def refs(config, args):
  """
  List all refs.
  """
  return config.repo.refs()


def show_refs(config, args):
  """
  Show refs supplied on stdin.
  """
  for item in lib.input_json_lines():
    yield config.repo.ref(item)


def delete_refs(config, args):
  """
  Delete refs supplied on stdin.
  """
  for ref_name in lib.input_json_lines():
    yield _delete_ref(config.repo, ref_name, args.force, args.dry_run)


def pull_requests(config, args):
  """
  List all PRs.
  """
  state = args.state or "open"
  return config.repo.pull_requests(state=state)


def contributors(config, args):
  """
  List all contributors.
  """
  return config.repo.contributors()


def stale_pr_branches(config, args):
  """
  List "stale" branches that associated with a closed PR and are from the same (non-forked) repository as the base.
  """
  repo = config.repo
  for pr in repo.pull_requests(state="closed"):
    is_stale = False
    if pr.head.repo == pr.base.repo:
      branch = repo.branch(pr.head.ref)
      if branch:
        is_stale = True
    if is_stale:
      yield {
        "html_url": pr.html_url,
        "base_branch": pr.base.ref,
        "head_branch": pr.head.ref,
      }
