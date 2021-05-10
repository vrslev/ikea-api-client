# -*- coding: utf-8 -*-
from setuptools import setup

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

setup(
	name='ikea_api',
	version='0.0.4',
	description='IKEA Api Client',
    url='https://github.com/vrslev/ikea-api-client',
	author='vrslev',
	author_email='5225148+vrslev@users.noreply.github.com',
    license='MIT',
	packages=['ikea_api', 'ikea_api.endpoints', 'ikea_api.misc'],
	install_requires=install_requires
)
