from ghizmo.commands import lib

import os
import yaml
import urllib.parse
from collections import defaultdict

_AUTHORS_INFO_FILES = ["authors-info.yml", "authors-info.json", "admin/authors-info.yml", "admin/authors-info.json"]


def assemble_authors(config, args):
  """
  Assemble a list of authors as an AUTHORS.md file based on GitHub repo history and a
  authors-info.{yml,json} file. Supports roles (for each person) and groups of people
  (leads, contributors, etc.).
  """
  github = config.github
  repo = config.repo
  authors_info_filename = None
  for filename in _AUTHORS_INFO_FILES:
    if os.path.isfile(filename):
      authors_info_filename = filename

  header = None
  footer = None
  groups = []
  exclude = []
  # Assemble roles, keyed by login.
  roles = {}
  if authors_info_filename:
    yield lib.status("Info from: %s" % authors_info_filename)
    with open(authors_info_filename, "r", encoding="utf-8") as f:
      info = yaml.safe_load(f)
      header = info.get("header")
      footer = info.get("footer")
      roles = info.get("roles")
      groups = info.get("groups")
      exclude = info.get("exclude")
    yield {"roles": roles, "groups": groups}
  else:
    yield lib.status("No roles file")

  login_to_user = {}
  for contributor in repo.contributors():
    user = github.user(contributor.login)
    login_to_user[user.login] = user

  # If any roles are listed but were somehow missing from the contributors return by the API
  # (for example the commits weren't linked up to the account properly), include them too.
  contributors_found = {contributor.login for contributor in repo.contributors()}
  unknown_contributors = []
  for login in roles:
    if login not in contributors_found:
      user = github.user(login)
      if user:
        yield lib.status("Author has a role but is not returned by GitHub as a contributor: %s (%s)" % (login, user))
      else:
        yield lib.status("Author has a role but is not a contributor or a known user: %s [%s]" % (user, type(user)))
        unknown_contributors.append(login)

      login_to_user[login] = user

  yield lib.status("Found %s authors" % len(login_to_user))
  yield lib.status("Found without GitHub user info: %s" % unknown_contributors)

  # Get a list of each group of logins.
  grouped_authors = [[] for g in groups]
  default_group = None
  assigned_logins = set()
  for count, group in enumerate(groups):
    yield lib.status("Group %s: %s" % (count, group))
    group["number"] = count
    if "members" in group:
      members = group["members"]
      assert isinstance(members, list)
      lib.status("members %s" % members)
      for login in members:
        grouped_authors[count].append(login)
        assigned_logins.add(login)
    else:
      yield lib.status("group has no members: %s %s %s" % (count, group, grouped_authors[count]))
      default_group = grouped_authors[count]

  yield {"all_logins": list(login_to_user.keys()), "assigned_logins": list(assigned_logins)}

  # Put all unassigned logins into last group.
  assert default_group is not None, "must have a group with no explicit members for unassigned contributors"
  default_group.extend(set(login_to_user.keys()).difference(assigned_logins))

  # Sort each group alphabetically by login.
  for logins in grouped_authors:
    logins.sort(key=lambda login: login.lower())

  def format_user(login, name):
    if login and name:
      return "%s (%s)" % (name, login)
    elif login:
      return login
    else:
      raise ValueError("Missing login name")

  commit_tallies = {}
  for stat in repo.contributor_statistics():
    yield lib.status("contrib stat: login '%s' total '%s'" % (stat.author.login, stat.total))
    commit_tallies[stat.author.login] = stat.total

  yield lib.status("Read %s contributor stats" % len(commit_tallies))

  issue_tallies = defaultdict(int)
  for issue in repo.issues(state="all"):
    issue_tallies[issue.user.login] += 1

  yield lib.status("Read %s issues/PRs" % len(issue_tallies))

  yield {"commit_tallies": commit_tallies, "issue_tallies": issue_tallies}

  with open("AUTHORS.md", "w", encoding="utf-8") as f:
    f.write("# Authors\n\n")
    if header:
      f.write("%s\n\n" % header)
    for group_number, logins in enumerate(grouped_authors):

      f.write("\n*%s*\n\n" % groups[group_number]["name"])

      for login in logins:
        user = login_to_user.get(login)
        role = roles.get(login)

        name = user.name if user else None
        if login in exclude:
          continue

        user_url = "https://github.com/%s" % login if user else None
        # Link to commits by that author
        commits_count = commit_tallies.get(login, 0)
        commits_url = "%s/commits?author=%s" % (repo.html_url, urllib.parse.quote_plus(login))
        # Link to issues and PRs by that author.
        issues_count = issue_tallies.get(login, 0)
        issues_url = "%s/issues?q=%s" % (repo.html_url, urllib.parse.quote_plus("author:%s" % login))

        yield lib.status("login '%s' commits %s issues %s" % (login, commits_count, issues_count))

        user_link = format_user(login, name)
        if user_url:
          user_link = "[%s](%s)" % (user_link, user_url)
        f.write("* %s" % user_link)
        if commits_count or issues_count:
          f.write(" — [%s+](%s)/[%s+](%s)" % (commits_count, commits_url, issues_count, issues_url))
        if role:
          f.write(" — _%s_" % role)
        f.write("\n")

    if footer:
      f.write("\n%s\n\n" % footer)

    f.write("\n(This file was auto-generated by [ghizmo assemble-authors](https://github.com/jlevy/ghizmo).)")
