#!/usr/bin/env

from setuptools import setup, find_packages
from ghizmo import main

setup(
  name="ghizmo",
  version=main.VERSION,
  packages=find_packages(),
  author="Joshua Levy",
  license="Apache 2",
  url="https://github.com/jlevy/ghizmo",
  install_requires=["github3.py>=1.0.0a2", "PyYAML>=3.11", "functools32>=3.2.3"],
  description=main.DESCRIPTION,
  long_description=main.LONG_DESCRIPTION,
  classifiers=[
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: System Administrators',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX',
    'Operating System :: Unix',
    'Programming Language :: Python :: 2.7',
    'Topic :: Utilities',
    'Topic :: Software Development'
  ],
  entry_points={
    "console_scripts": [
      "ghizmo = ghizmo.main:main",
    ],
  },
)
