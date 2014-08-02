from bacondegrees.bacondegrees import prep
from setuptools import setup

prep()

setup(
	name = 'bacondegrees',
	packages = ['bacondegrees'],
	package_data = {
		'': ['*.db']
		},
	entry_points = {
		'console_scripts': ['bacondegrees = bacondegrees.bacondegrees:main']
		},
	version = '0.1.0',
	description = 'A simple command line tool for finding degrees on Kevin Bacon.',
	long_description = open('README.md', 'r').read(),
	author = 'Chris Lock',
	author_email = 'chris@bright.is',
	url = 'https://github.com/chris-lock/bacondegrees',
	)