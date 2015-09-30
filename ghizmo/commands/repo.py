from __future__ import print_function

from ghizmo.commands import lib


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


def branches_full(config, args):
  """
  List full info about all branches.
  """
  for b in config.repo.branches():
    yield config.repo.branch(b.name)


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


def collaborators(config, args):
  """
  List all collaborators.
  """
  return config.repo.collaborators()


def releases(config, args):
  """
  List all releases.
  """
  return config.repo.releases()


def create_release(config, args):
  """
  Create a new release.
  """
  yield config.repo.create_release(args.tag_name, name=args.name,
                                   target_commitish=args.get("target_commitish"), body=args.get("body"),
                                   draft=args.get_bool("draft"), prerelease=args.get_bool("prerelease"))
