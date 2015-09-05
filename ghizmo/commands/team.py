from __future__ import print_function

from ghizmo.commands import lib

def teams(config, args):
  """
  List teams in a given organization.
  """
  return config.github.organization(args.org_name).teams()
