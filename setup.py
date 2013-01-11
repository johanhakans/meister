#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(name='Meister',
      version='0.1',
      description='Keep track of complex cloud setups.',
      author='Fabian Sörqvist',
      author_email='fabian.sorqvist@wunderkraut.com',
      url='https://github.com/WKLive/meister',
      packages=find_packages(),
      install_requires=['fabric>=1.0', "apache-libcloud>=0.10", "pyyaml"],
      tests_require=["nose"],
      entry_points={
        'console_scripts': [
            'meister = meister.main:main',
        ]
      },
 )

