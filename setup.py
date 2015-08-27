#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# Date  : 2015-08-27
# Author: Master Yumi
# Email : yumi@meishixing.com

from version import VERSION
try:
    from setuptools import setup
except ImportError:
    pass

setup(
    name = 'chiffon',
    version = VERSION,
    keywords = ('api frome work', 'chiffon'),
    description = 'The API Framework For THack',
    author = 'Mr.Eleven',
    packages = [ '.', 'chiffon'],
    zip_safe=False
    )

