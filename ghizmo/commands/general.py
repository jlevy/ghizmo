def rate_limit(config, args):
  """
  Current rate limit information.
  """
  yield config.github.rate_limit()


def emojis(config, args):
  """
  List available emojis.
  """
  yield config.github.emojis()


def octocat(config, args):
  """
  Easter egg.
  """
  yield config.github.octocat(say=args.get("say"))


def zen(config, args):
  """
  Easter egg.
  """
  yield config.github.zen()
