#!/usr/bin/env python

import setuptools  # for side-effects to make 'python setup.py develop' work
from setuptools import setup
from setuptools import Command

# To generate the runtests.py script:
# py.test --genscript=runtests.py


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys
        import subprocess
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)


if __name__ == "__main__":
    setup(name="db",
          version="0.0.1",
          description="Databases for Humans",
          author="John Evans",
          author_email="lgastako@gmail.com",
          url="https://github.com/lgastako/db",
          provides=["db"],
          packages=["db"],
          cmdclass={"test": PyTest},
          classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Programming Language :: SQL",
            "Programming Language :: Python :: 2",
            "Topic :: Database",
            "Topic :: Software Development :: Libraries",
          ])
