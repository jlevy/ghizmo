from ghizmo.commands import lib


def show_users(config, args):
  """
  Show user info for usernames supplied on stdin.
  """
  for item in lib.input_json_lines():
    yield config.github.user(item)


def search_users(config, args):
  """
  Search for users.
  """
  config.github.search_users(query=args.query,
                             sort=args.get("sort"), order=args.get("order"),
                             per_page=args.get_int("per_page", None),
                             text_match=args.get_bool("text_match"), number=args.get_int("number", None),
                             etag=args.get("etag"))
