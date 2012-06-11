#!/usr/bin/env python

import setuptools  # for side-effects to make 'python setup.py develop' work
from setuptools import setup
from setuptools import Command


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys,subprocess
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)


if __name__ == "__main__":
    setup(name="db",
          version="0.0.1",
          description="Queries for Humans",
          author="John Evans",
          author_email="lgastako@gmail.com",
          provides="db",
          cmdclass={"test": PyTest})
