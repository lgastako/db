#!/usr/bin/env python

import os
from setuptools import setup
from setuptools import find_packages


if __name__ == "__main__":
    setup(name="db",
          version="0.0.7",
          description="Databases for Humans",
          author="John Evans",
          author_email="lgastako@gmail.com",
          url="https://github.com/lgastako/db",
          install_requires=["antiorm"],
          packages=find_packages(),
          provides=["db"])
