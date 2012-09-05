#!/usr/bin/env python

import os
from setuptools import setup
from setuptools import find_packages


with open("requirements.txt") as f:
    requirements = [req.strip() for req in f]


if __name__ == "__main__":
    setup(name="db",
          version="0.0.2",
          description="Databases for Humans",
          author="John Evans",
          author_email="lgastako@gmail.com",
          install_requires=requirements,
          packages=find_packages(),
          provides=["db"])
