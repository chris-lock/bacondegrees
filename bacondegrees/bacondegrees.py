import optparse
import sys
from bacontree import BaconTree
import os

baconTree = BaconTree()

## This routes the CLI options and arguments. Since arguments passed into
#  options are pulled out during parsing, we need to check them against
#  sys.argv so we don't run baconTree.get when a user is running an option.
#
#  @return void
def main():
	parser = addParserOptions(optparse.OptionParser())

	(options, arguments) = parser.parse_args()
	argumentsCountUnparsed = len(arguments)
	argumentsCount = len(sys.argv[1:])

	if (argumentsCountUnparsed == 1 and
			argumentsCount == argumentsCountUnparsed):
	 	baconTree.get(arguments[0])

	elif argumentsCount == 0:
		printHeader()
		parser.print_help()

def addParserOptions(parser):
	optionsDegrees = optparse.OptionGroup(
		parser,
		'Eat Your Bacon',
		'If plain old bacon isn\'t good enough',
		)
	optionsDegrees.add_option(
		'-g',
		'--grassfed',
		help = 'Delicious organic bacon with caching to speed up future '
			'queries.',
		action = 'callback',
		callback = getWithCaching,
		type = 'string',
		metavar = 'name'
		)
	optionsDegrees.add_option(
		'-s',
		'--swanson',
		help = 'For those who literally want all the possible bacon.',
		action = 'callback',
		callback = complete
		)
	optionsDegrees.add_option(
		'-v',
		'--vegan',
		help = 'Find those few people who have nothing to do with bacon.',
		action = 'callback',
		callback = getExceptions
		)
	parser.add_option_group(optionsDegrees)

	optionsDatabase = optparse.OptionGroup(
		parser,
		'Prepare Your Bacon',
		'Not happy with your bacon? All you need is a tar containing json '
			'files formatted film.name, cast[].name',
		)
	optionsDatabase.add_option(
		'-b',
		'--burn',
		help = 'Oh, no! You\'re bacon\'s burned. Better replace it with a new '
			'tar.',
		action = 'callback',
		callback = overwrite,
		type = 'string',
		metavar = 'tar.gz'
		)
	optionsDatabase.add_option(
		'-f',
		'--flip',
		help = 'That bacon\'s looking a little crispy. Why don\'t you update '
			'it with some fresh tar?',
		action = 'callback',
		callback = update,
		type = 'string',
		metavar = 'tar.gz'
		)
	parser.add_option_group(optionsDatabase)

	return parser

def printHeader():
	print('')
	print('  .########:+..__     _..######,')
	print(' ##########################+++###')
	print(':           \'""""""\'\'\'\'         :')
	print(':#+++++,._   __     ____.....++:')
	print('`############+++############+:"')
	print('        `""""""""""""\'')
	print('BACON' + u'\xb0')
	print('')
	print('Just pass in an actor\'s name and enjoy.')
	print('')
	print('')
	print('')

def getWithCaching(option, opt_str, value, parser):
	runAsRoot()
	baconTree.get(value, True)

def runAsRoot():
	if os.geteuid() != 0:
		arguments = ['sudo', sys.executable] + sys.argv + [os.environ]
		os.execlpe('sudo', *arguments)

def complete(option, opt_str, value, parser):
	runAsRoot()
	baconTree.complete()

def getExceptions(option, opt_str, value, parser):
	runAsRoot()
	baconTree.getExceptions()

def overwrite(option, opt_str, value, parser):
	runAsRoot()
	baconTree.overwrite(value)

def update(option, opt_str, value, parser):
	runAsRoot()
	baconTree.update(value)

def prep():
	baconTree.prep()