#!/usr/bin/env python

import setuptools  # for side-effects to make 'python setup.py develop' work
from setuptools import setup
from setuptools import Command


if __name__ == "__main__":
    setup(name="db",
          version="0.0.1",
          description="Databases for Humans",
          author="John Evans",
          author_email="lgastako@gmail.com",
          url="https://github.com/lgastako/db",
          provides=["db"],
          packages=["db", "db.drivers"],
          classifiers=["Development Status :: 4 - Beta",
                       "Intended Audience :: Developers",
                       "License :: OSI Approved :: MIT License",
                       "Operating System :: OS Independent",
                       "Programming Language :: SQL",
                       "Programming Language :: Python :: 2",
                       "Topic :: Database",
                       "Topic :: Software Development :: Libraries"])
