#!/usr/bin/env python3

from setuptools import setup, find_packages


setup(
    name='metrics-demo',
    version='1.0',
    description='Prometheus metrics in multiprocess server demo',
    author='Jan Seifert',
    author_email='jan.seifert@fotkyzcest.net',
    packages=find_packages(),
    install_requires=[
        'Django<3.2',
        'ipcqueue',
        'prometheus_client',
        'uwsgi',
    ],
)
