#!/usr/bin/env python                                                                                                                                        
from setuptools import setup, find_packages

setup(
	name="Opportunity",
	version='0.1',
	description='Charlie Hargoods opportunity system',
	author='Charlie Hargood, Darren Golbourn, Sina Samangooei',
	author_email='cah@ecs.soton.ac.uk,golbourn@gmail.com,ss@ecs.soton.ac.uk',
	packages=find_packages(),
	install_requires=[],
	test_suite="opportunity.test",
)