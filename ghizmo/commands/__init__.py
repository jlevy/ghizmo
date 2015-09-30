"""
This module holds the pre-defined commands.

Public functions here (not starting with '_') are auto-registered into Ghizmo's command line.

Best practices:
- Include a one-line pydoc, which will appear in the --help output.
- Yield results for items that search for information.
- Yield status for items that do things.

For the GitHub library API, see: https://github.com/sigmavirus24/github3.py
"""

__author__ = 'jlevy'

__all__ = ['repo', 'general', 'team', 'authors']
