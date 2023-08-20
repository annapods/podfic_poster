# -*- coding: utf-8 -*-
""" https://github.com/kennethreitz/setup.py """


from os.path import join, abspath, dirname
from setuptools import setup


here = abspath(dirname(__file__))


# Requirements from requirements.txt
requirements = []
try:
    with open(join(here, 'requirements.txt'), encoding='utf-8') as f:
        required = f.read().splitlines()
    requirements = [package.split("  #")[0] for package in required]
    requirements = [package for package in requirements if package]
except FileNotFoundError:
    pass

# Long description from README.md
with open(join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()


# Setup
setup(
    name = 'podfic_poster',
    version = '1.1.0',
    description = 'A podfic posting helper!',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    author = 'Annapods',
    author_email = 'annabelle.myrt@gmail.com',
    python_requires = '>=3.7.0',
    url = 'https://github.com/annapods/podfic_poster',
    packages = ["src", "cli"],
    install_requires = requirements,
    include_package_data = True
)
