from sys import exit, stdout
from time import time

def printAndExit(message):
	print('\a' + message)
	exit(1)

def bold(string):
	return u'\033[1m' + string + '\033[0m'

class Benchmark():
	startTime = None

	def __init__(self):
		pass

	def start(self):
		self.startTime = time()

	def end(self):
		return self.getTimeStamp(time() - self.startTime)

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

	def getPlural(self, value, measurement, endCharacter = ''):
		pluralize = '' if value == 1 else 's'

		return str(value) + ' ' + measurement + pluralize + endCharacter

def progressBar(itteration, total):
	def getProgressBar(current, total):
		steps = 19.0
		progress = int(float(current) / float(total) * steps)
		progressRemaining = int(steps) - progress

		return '[~' + ('~' * progress) + (' ' * progressRemaining) + ']'

	stdout.write('\r' + getProgressBar(itteration, total) +
			' (' + str(itteration) + '/' + str(total) + ')')
	stdout.flush()

def loading(itteration, speedReduction = 250):
	steps = 5
	itterationStep = int(itteration / speedReduction)
	loadingIcon = [' '] * steps
	loadingIcon[itterationStep % steps] = '~'

	stdout.write('\r[' + ''.join(loadingIcon) + ']')
	stdout.flush()

def loadingComplete(message):
	stdout.write('\r' + message + '\n')