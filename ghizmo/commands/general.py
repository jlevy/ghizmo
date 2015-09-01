from __future__ import print_function

from ghizmo.commands import lib

def stale_pr_branches(config, args):
  """
  List "stale" PR branches, i.e. those for a closed PR from the same, non-forked repository.
  """
  repo = config.repo
  for pr in repo.pull_requests(state="closed"):
    if pr.head.repo == pr.base.repo and repo.branch(pr.head.ref):
      yield {
        "html_url": pr.html_url,
        "base_branch": pr.base.ref,
        "head_branch": pr.head.ref,
      }
