#!/usr/bin/env python

from sys import exit, stdout
from time import time

## Helper functions for outputting to command line.
#
#  @author Chris Lock

## Sounds system noise, prints a message, and system exits.
#
#  @param {string} message The Message to print
#  @return void
def alertAndExit(message):
	printAndExit('\a' + message)

## Prints a message, and system exits.
#
#  @param {string} message The Message to print
#  @return void
def printAndExit(message):
	print(message)
	exit(1)

## Bolds a given string when printed in terminal.
#
#  @param {string} string The string to to bold
#  @return {string} The bolded string
def bold(string):
	return u'\033[1m' + string + '\033[0m'

## A class for printing a performace benchmark.
class Benchmark():
	startTime = None

	## Empty constructor.
	#
	#  @return void
	def __init__(self):
		pass

	## Starts the benchmark timer.
	#
	#  @param {object} self The object
	#  @return void
	def start(self):
		self.startTime = time()

	## Prints the formatted benchmark timestamp.
	#
	#  @param {object} self The object
	#  @return void
	def end(self):
		if self.startTime:
			return self.getTimeStamp(time() - self.startTime)

		return 'No benchmark started.'

	## Formats a raw timestamp as a string with X Hours, X Minutes, and X
	#  seconds.
	#
	#  @param {object} self The object
	#  @param {float} secondsRaw The time() you want formatted
	#  @return {string} The formatted time stamp
	def getTimeStamp(self, secondsRaw):
		minutes, seconds = divmod(secondsRaw, 60)
		hours, minutes = divmod(minutes, 60)
		timeStamp = self.getPlural(seconds, 'second')

		if minutes:
			endCharacter = ', and ' if hours else ' and '
			timeStamp = (self.getPlural(int(minutes), 'minute', endCharacter) +
					timeStamp)
		else:
			return timeStamp

		if hours:
			timeStamp = self.getPlural(int(hours), 'hour', ', ') + timeStamp

		return timeStamp

	## Gets the plural version of a measurement if more than one.
	#
	#  @param {object} self The object
	#  @param {int} secondsRaw The time() you want formatted
	#  @param {string} measurement The measurement the pluralize
	#  @param {string} endCharacter used to add spaces after the word
	#  @return {string} The plural or non-plural version
	def getPlural(self, value, measurement, endCharacter = ''):
		pluralize = '' if value == 1 else 's'

		return str(value) + ' ' + measurement + pluralize + endCharacter

## Prints a progress bar for a given itteration out of a total number of
#  itterations.
#
#  @param {int} itteration The current itteration
#  @param {int} total The total number of itterations
#  @return void
def progressBar(itteration, total):
	## Get's the ascii representation of the progress bar.
	#
	#  @param {int} itteration The current itteration
	#  @param {int} total The total number of itterations
	#  @return {string} The progress bar
	def getProgressBar(current, total):
		steps = 19.0
		progress = int(float(current) / float(total) * steps)
		progressRemaining = int(steps) - progress

		return '[~' + ('~' * progress) + (' ' * progressRemaining) + ']'

	stdout.write('\r' + getProgressBar(itteration, total) +
			' (' + str(itteration) + '/' + str(total) + ')')
	stdout.flush()

## Prints a loading icon for a given itteration.
#
#  @param {int} itteration The current itteration
#  @param {int} speedReduction A scalar to slow the speed by
#  @return void
def loading(itteration, speedReduction = 250):
	steps = 5
	itterationStep = int(itteration / speedReduction)
	loadingIcon = [' '] * steps
	loadingIcon[itterationStep % steps] = '~'

	stdout.write('\r[' + ''.join(loadingIcon) + ']')
	stdout.flush()

## A function to consolidate all the outputs at the end of loading.
#
#  @param {string} message The message to print
#  @return void
def loadingComplete(message):
	stdout.write('\r' + message + '\n')