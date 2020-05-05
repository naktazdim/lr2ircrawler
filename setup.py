#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='lr2ircrawler',
    version='1.1',
    description='LR2 Internet Ranking Crawler',
    author='nakt',
    author_email='nakt@walkure.net',
    install_requires=['luigi', 'pandas', 'requests', 'more_itertools'],
    python_requires='>=3.7',
    packages=find_packages(exclude=('tests', 'docs')),
    test_suite='tests'
)
