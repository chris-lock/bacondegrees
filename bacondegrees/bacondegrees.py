#!/usr/bin/env python

import optparse
import sys
from bacondegreescore import BaconDegreesCore
from baconhelpers import bold
import os

# @type {object} An instance of the controller
baconDegreesCore = BaconDegreesCore()

## This routes the CLI options and arguments. Since arguments passed into
#  options are pulled out during parsing, we need to check them against
#  sys.argv so we don't run baconDegreesCore.get when a user is running an 
#  option.
#
#  @return void
def main():
	parser = addParserOptions(optparse.OptionParser())

	(options, arguments) = parser.parse_args()
	argumentsCountUnparsed = len(arguments)
	argumentsCount = len(sys.argv[1:])

	if (argumentsCountUnparsed == 1
			and argumentsCount == argumentsCountUnparsed):
	 	baconDegreesCore.get(arguments[0])

	elif argumentsCountUnparsed > 1:
		print('Too many arguments. Make sure you pass a string in quotes.\n')
		parser.print_help()

	elif argumentsCount == 0:
		printHeader()
		parser.print_help()

## Adds options to optparse.
#
#  @param {object} parser The optparse.OptionParser() object
#  @return The optparse object
def addParserOptions(parser):
	optionsDatabase = optparse.OptionGroup(
		parser,
		'Prepare Your Bacon',
		'Not happy with your bacon? All you need is a tar containing json '
			'files formatted film.name, cast[].name',
		)
	optionsDatabase.add_option(
		'-c',
		'--cook',
		help = 'Raw bacon?! Never. You need to cook it so you have some movies '
				'to work with. If you do a search before running this, it\'ll '
				'be run then.',
		action = 'callback',
		callback = prep,
		)
	optionsDatabase.add_option(
		'-b',
		'--burn',
		help = 'Oh, no! Your bacon\'s burned. Better replace it with a new '
				'tar.',
		action = 'callback',
		callback = overwrite,
		type = 'string',
		metavar = 'tar.gz',
		)
	optionsDatabase.add_option(
		'-f',
		'--flip',
		help = 'That bacon\'s looking a little crispy. Why don\'t you update '
				'it with some fresh tar?',
		action = 'callback',
		callback = update,
		type = 'string',
		metavar = 'tar.gz',
		)
	parser.add_option_group(optionsDatabase)

	optionsDegrees = optparse.OptionGroup(
		parser,
		'Eat Your Bacon',
		'If plain old bacon isn\'t good enough',
		)
	optionsDegrees.add_option(
		'-g',
		'--grassfed',
		help = 'Delicious organic bacon with caching to speed up future '
				'queries. Recommended by both me and your doctor.',
		action = 'callback',
		callback = getWithCaching,
		type = 'string',
		metavar = 'name',
		)
	optionsDegrees.add_option(
		'-s',
		'--swanson',
		help = 'For those who literally want all the possible bacon. This\'ll '
				'take a while',
		action = 'callback',
		callback = complete,
		)
	optionsDegrees.add_option(
		'-v',
		'--vegan',
		help = 'Find those few people who have nothing to do with bacon.',
		action = 'callback',
		callback = getExceptions,
		)
	parser.add_option_group(optionsDegrees)

	return parser

## Prints the header for the app.
#
#  @return void
def printHeader():
	print(''
			'\n  .########:+..__     _..######,'
			'\n ##########################+++###'
			'\n:           \'""""""\'\'\'\'         :'
			'\n:#+++++,._   __     ____.....++:'
			'\n`############+++############+:"'
			'\n        `""""""""""""\''
			'\n' + bold('BACON' + u'\xb0') + ''
			'\n'
			'\nJust pass in an actor\'s name and enjoy.'
			'\n'
			'\n')

## Preps the database for module installation.
#
#  @param {object} parser The instance causing the callback
#  @param {string} opt_str The option string from the command line
#  @param {string} value The argument value associated with the option
#  @param {object} parser The instance doing the parsing work
#  @return void
def prep(option, opt_str, value, parser):
	print(type(option), type(opt_str), type(value), type(parser))
	return
	baconDegreesCore.prep(True)

## Preps the database for module installation.
#
#  @param {object} parser The instance causing the callback
#  @param {string} opt_str The option string from the command line
#  @param {string} value The argument value associated with the option
#  @param {object} parser The instance doing the parsing work
#  @return void
def overwrite(option, opt_str, value, parser):
	runAsRoot()
	baconDegreesCore.overwrite(value)

## Runs the previous command as root. Once the module is installed we need this
#  as the database will be readonly otherwise.
#
#  @return void
def runAsRoot():
	if os.geteuid() != 0:
		arguments = ['sudo', sys.executable] + sys.argv + [os.environ]
		os.execlpe('sudo', *arguments)

## Updates the database with a new tar.gz contaontaining json files formatted 
#  film.name, cast[].name.
#
#  @param {object} parser The instance causing the callback
#  @param {string} opt_str The option string from the command line
#  @param {string} value The argument value associated with the option
#  @param {object} parser The instance doing the parsing work
#  @return void
def update(option, opt_str, value, parser):
	runAsRoot()
	baconDegreesCore.update(value)

## Gets the current actor name and caches all actors found on the way.
#
#  @param {object} parser The instance causing the callback
#  @param {string} opt_str The option string from the command line
#  @param {string} value The argument value associated with the option
#  @param {object} parser The instance doing the parsing work
#  @return void
def getWithCaching(option, opt_str, value, parser):
	runAsRoot()
	baconDegreesCore.get(value, True)

## Completes the entire tree from Kevin Bacon and caches all the results.
#
#  @param {object} parser The instance causing the callback
#  @param {string} opt_str The option string from the command line
#  @param {string} value The argument value associated with the option
#  @param {object} parser The instance doing the parsing work
#  @return void
def complete(option, opt_str, value, parser):
	runAsRoot()
	baconDegreesCore.complete()

## Completes the entire tree from Kevin Bacon and caches all the results. Then
#  finds all the exceptions.
#
#  @param {object} parser The instance causing the callback
#  @param {string} opt_str The option string from the command line
#  @param {string} value The argument value associated with the option
#  @param {object} parser The instance doing the parsing work
#  @return void
def getExceptions(option, opt_str, value, parser):
	runAsRoot()
	baconDegreesCore.getExceptions()