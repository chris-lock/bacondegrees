from baconsearch import BaconSearch
from baconupdate import BaconUpdate
from baconpyramid import BaconPyramid
from time import time

class BaconDegreesCore():
	baconSearch = BaconSearch()
	baconUpdate = BaconUpdate()
	baconPyramid = BaconPyramid()
	time = 0

	def __init__(self):
		pass

	def prep(self, *args):
		self.baconUpdate.prep(*args)

	def update(self, tarFileForUpdate):
		self.baconUpdate.update(tarFileForUpdate)

	def get(self, actorName, useCaching = False):
		self.prep()
		self.time = time()

		if (actorName == 'Chris Lock'):
			return self.showBestResults(actorName)

		if (actorName == 'Kevin Bacon'):
			return self.showResults(actorName, 0, ['He is himself.'])

		self.baconSearch.setup().start()
		actorRow = self.baconSearch.getActorByName(actorName)
		self.baconSearch.end()

		if not actorRow:
			return self.showNoResults(actorName)

		actorPath = actorRow['Path']

		if actorPath:
			return self.parsePath(actorPath)

		actorPath = self.baconPyramid.find(actorRow['ActorId'], useCaching)

		if actorPath:
			return self.parsePath(actorPath)

		return self.showUnsolvableResult(actorName)

	def showBestResults(self, actorName, isFemale = False):
		(shehe, shehim) = ('She', 'her') if isFemale else ('He', 'him')

		print('\a\a\a*-._.\' ' + actorName.upper() + ' \'._.-*'
				'\n?!?!?!?!'
				'\n' + shehe + '\'s soooo dreamy...'
				'\nI saw ' + shehim + ' in this coffee shop on Orachard last '
				'Sunday.')

	def showResults(self, actorName, degrees, path):
		print(actorName + ' is ' + str(degrees) + u'\xb0')

		for degree in path:
			print(degree)

	def showNoResults(self, actorName):
		print('I couldn\'t find \'' + actorName + '\'.'
			'\nAre you sure that\'s someone in Hollywood? I\'ve never heard of '
			'them.')

	def parsePath(self, path):
		print(time() - self.time)
		films = {}
		# print(self.baconSearch.getFilmsById(path['films']))
		# print(self.baconSearch.getActorsById(path['actors']))

		# print(path)

	def getFilmsDictionary(self):
		pass

	def showUnsolvableResult(self, actorName):
		noConnection = ('Inconceivable! ' + actorName + ' has no connection to '
			'Kevin Bacon.')

		self.showResults(actorName, 'Infinity', [noConnection])

	def complete(self):
		self.prep()
		print('Wait, wait. I worry what you just heard was, "Give me a lot of '
			'bacon"...')

	def overwrite(self, tarFileForOverwite):
		self.baconUpdate.overwrite(tarFileForOverwite)