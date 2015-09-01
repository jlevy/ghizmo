# Ghizmo

GitHub's APIs are great, but the friction to using them is often a bit high.
You have to look up which library is best, then write code by hand to use that library,
wasting time on setup, authentication, etc.

Ghizmo is a simple command-line harness to do more complex things with the GitHub APIs,
layered on top of the simple and clean [github3.py](https://github.com/sigmavirus24/github3.py)
library. It's also easy to add more commands.

It differs from [hub](https://github.com/github/hub) in that it's not focusing on just
a few key features. Rather, it's just a way to use the full APIs more easily, and writing
data in JSON that's modeled directly off the APIs. Also, since it's in Python instead of Go,
it can be extended without a compile step.

## Examples

Basic access to API, showing responses in JSON:

```
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

Combine with other tools:
```
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
```
$ ghizmo branches
{
  "commit": {
    "sha": "4c41820409e9394778b7b17d9b831f81d51a03bc", 
    "url": "https://api.github.com/repos/jlevy/ghizmo/commits/4c41820409e9394778b7b17d9b831f81d51a03bc"
  }, 
  "name": "master"
}
```

More complex commands can be defined easily.
This command looks for non-deleted branches on closed PRs.
```
$ ghizmo stale-pr-branches > stale-branches.json
$ # Edit/review, then actually do it.
$ jq '.head_branch' stale-pr-branches.json | ghizmo delete-branches --dry-run 
Delete reference: heads/aaa
Delete reference: heads/bbb
...
$ jq '.head_branch' stale-pr-branches.json | ghizmo delete-branches
Delete reference: heads/aaa
Delete reference: heads/bbb
...
$
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
password. To do this, add a `~/.ghizmo.yml` file:

```
# Ghizmo configuration
# Default GitHub login name:
username: my-github-id
# Personal access token for the above GitHub account:
access_token: aaaaaaaaaabbbbbbbbbbbccccccccc1234567890
```

Create an access token [here](https://github.com/settings/tokens) to use with Ghizmo.


## Maturity

One-day hack. Could be extended a lot, but seems to work.
