#!/usr/bin/env python

import os
from setuptools import setup

with open('requirements.txt') as f:
    requirements = [req.strip() for req in f]


if __name__ == "__main__":
    setup(name="db",
          version=os.environ.get('MILOVERSION'),
          description="Databases for Humans",
          author="John Evans",
          author_email="lgastako@gmail.com",
          install_requires=requirements,
          provides=["db"])
