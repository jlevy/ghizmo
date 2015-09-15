# Ghizmo

![Octopus hose](images/xk8-octopus-hose-180.png)

Ghizmo is an extensible command line for GitHub.

[GitHub's APIs](https://developer.github.com/v3/)
are exceptionally powerful, but the friction to using them can be a bit high.
You have to [look up which library is best](https://developer.github.com/libraries/),
then write code to use that library,
spending time on trial and error with setup, authentication, etc.
Once you get something working, the result is probably not a reusable script without additional effort.

Ghizmo lets you do complex things with the GitHub APIs from the command line,
so you can automate reading, creating, or managing GitHub
repos, contributor statistics, pull requests, teams, etc.
Its JSON output is modeled directly off the APIs,
and can be piped into other tools.
It's also easy to add, save, and share more commands you perform frequently,
by putting them into a simple `ghizmo_commands.py` file,
and they become automatically available.

Essentially, it's just a harness around the clean and complete [github3.py](https://github.com/sigmavirus24/github3.py) library.
It differs from the standard option [hub](https://github.com/github/hub) in that it's not focusing key features to augment the `git` command.
Rather, it's a way to use the full GitHub APIs more easily.
(Also, since it's in Python, not Go, it can be extended without a compile step.)

## Examples

Commands are all defined [here](ghizmo/commands) and [below](#custom-commands).

Run `ghizmo --help` for a list of commands -- and see below on how to add new commands.

### Simple commands

Basic access to API, showing responses in JSON:

```bash
$ ghizmo tags --repo torvalds/linux
{
  "commit": {
    "sha": "c13dcf9f2d6f5f06ef1bf79ec456df614c5e058b",
    "url": "https://api.github.com/repos/torvalds/linux/commits/c13dcf9f2d6f5f06ef1bf79ec456df614c5e058b"
  },
  "name": "v4.2-rc8",
  "tarball_url": "https://api.github.com/repos/torvalds/linux/tarball/v4.2-rc8",
  "zipball_url": "https://api.github.com/repos/torvalds/linux/zipball/v4.2-rc8"
}
...
```

The advantage to JSON is it's easy to combine with other tools.
Here's a histogram of number contributions for all Linux kernel contributors:

```bash
$ ghizmo tags --repo torvalds/linux | jq '.tarball_url' | head -1
"https://api.github.com/repos/torvalds/linux/tarball/v4.2-rc8"
...
$ ghizmo contributors --repo torvalds/linux | jq '.contributions' | histogram.py -B400,800,1600,3200,6400 -p
# NumSamples = 232; Min = 207.00; Max = 15475.00
# Mean = 792.982759; Variance = 1594202.232461; SD = 1262.617215; Median 464.500000
# each ∎ represents a count of 1
  207.0000 -   400.0000 [   100]: ∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎ (43.10%)
  400.0000 -   800.0000 [    68]: ∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎ (29.31%)
  800.0000 -  1600.0000 [    47]: ∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎ (20.26%)
 1600.0000 -  3200.0000 [    10]: ∎∎∎∎∎∎∎∎∎∎ (4.31%)
 3200.0000 - 15475.0000 [     7]: ∎∎∎∎∎∎∎ (3.02%)
```

You may skip the `--repo` option and Ghizmo will infer the current repository if you are in a working directory with a GitHub origin:

```bash
$ ghizmo branches
{
  "commit": {
    "sha": "4c41820409e9394778b7b17d9b831f81d51a03bc",
    "url": "https://api.github.com/repos/jlevy/ghizmo/commits/4c41820409e9394778b7b17d9b831f81d51a03bc"
  },
  "name": "master"
}
$ ghizmo releases
...
```

### Command arguments

Commands can take arguments.
This command lists teams, and requires an organization name
(should you forget an argument required by a command, you'll be rudely advised of your oversight):

```bash
$ ghizmo teams -a org_name=OctoTech
{
  "description": "OctoTech",
  "id": 999,
  "members_url": "https://api.github.com/teams/999/members{/member}",
  "name": "Owners",
  "permission": "admin",
  "repositories_url": "https://api.github.com/teams/999/repos",
  "slug": "owners",
  "url": "https://api.github.com/teams/999"
}
```

It's also helpful for scripting releases:

```bash
$ ghizmo create-release -a name=0.9.99 -a tag_name=0.9.99 -a prerelease=true
```

### A more complex example

If you've ever had a messy GitHub repository to clean up, you might like this command,
which looks for non-deleted branches on closed PRs.
```bash
$ ghizmo stale-pr-branches > stale-pr-branches.json
```

You edit/review that file, then test and perform deletions:

```
$ jq '.head_branch' stale-pr-branches.json | ghizmo delete-branches --dry-run
{
  "message": "Deleted heads/aaa",
  "dry_run": true
}
...
$ jq '.head_branch' stale-pr-branches.json | ghizmo delete-branches
{
  "message": "Deleted heads/aaa",
  "dry_run": false
}
...
```

## Installation

Requires Python 2.7+. Then (with sudo if desired):

```
pip install ghizmo
```

Ghizmo benefits if `git` is in your path so it can auto-detect your repository config.
You may also want to install tools like
[`jq`](https://github.com/stedolan/jq) or [data_hacks](https://github.com/bitly/data_hacks)
so you can perform operations such as the ones above that process JSON outputs.


## Configuration

You can supply username and password from the command line, but you probably want to be able to use APIs without typing your
password. To do this, create a `~/.ghizmo.yml` file:

```yaml
# Ghizmo configuration
# Default GitHub login name:
username: my-github-id
# Personal access token for the above GitHub account:
access_token: aaaaaaaaaabbbbbbbbbbbccccccccc1234567890
```

Create an access token on [your GitHub settings page](https://github.com/settings/tokens) to use with Ghizmo.

## Custom commands

To add a new command, create a file `ghizmo_commands.py` in your current directory.
For example, here is one that counts pull requests by user:

```python
import ghizmo.commands.lib as lib
from collections import defaultdict

def count_prs(config, args):
  """
  Show tallies of pull requests by author login name.
  """
  counts = defaultdict(int)
  for pr in config.repo.pull_requests(state="closed"):
    counts[pr.user.login] += 1
    yield { "status": "I'm at PR %s!" % pr.number }

  yield counts

def octotech_create_repo(config, args):
  """
  If you like, your command can be custom, e.g. to your organization.
  This creates a repo within your org owned by a specific team.
  """
  org = config.github.organization("OctoTech")
  team_id = 1234567890  # OctoTech engineering team
  repo = org.create_repository(args.name, description=args.description, private=True,
    has_issues=False, has_wiki=False, team_id=team_id)
```

Now running
```bash
ghizmo count-prs
```
(note the dash) will stream JSON messages as it tallies,
then write a tally of closed PRs for each user.

To use the second command, you need to specify custom arguments:

```bash
ghizmo octotech-create-repo -a name=ninth-leg -a description="Yet another repository!"
```

## Convenience

The idea here is both to provide simple commands, but also to allow more custom or complex use.
You can easily save/commit commands you write to `ghizmo_commands.py` file to Git,
and your teammates can then use the same commands.
This means you can automate setup and configuration of GitHub repositories, teams, etc. in a flexible way.
If there're generally useful, please submit a PR and I'll gladly merge it for use by everyone.

## Maturity

Mostly a one-day hack. Could be extended a lot, but seems to work.

## Contributing

Yes, please!
We need more commands in the library.
File issues for bugs or general discussion.

## License

Apache 2
