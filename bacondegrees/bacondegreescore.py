from baconsearch import BaconSearch
from baconupdate import BaconUpdate
from baconpyramid import BaconPyramid
from baconhelpers import Benchmark, bold, loadingComplete
from sys import stdout

class BaconDegreesCore():
	baconSearch = BaconSearch()
	baconUpdate = BaconUpdate()
	baconPyramid = BaconPyramid()
	benchmark = Benchmark()

	def __init__(self):
		pass

	def prep(self, *args):
		self.baconUpdate.prep(*args)

	def update(self, tarFileForUpdate):
		self.baconUpdate.update(tarFileForUpdate)

	def get(self, actorName, useCaching = False):
		self.prep()
		self.benchmark.start()

		if (actorName == 'Chris Lock'):
			return self.showBestResults(actorName)

		if (actorName == 'Kevin Bacon'):
			return self.showResults(actorName, 0, ['He is himself.'])

		self.baconSearch.setup().start()
		actorRow = self.baconSearch.getActorByName(actorName)
		self.baconSearch.end()

		if not actorRow:
			return self.showNoResults(actorName)

		actorNameProper = actorRow['ActorName']
		actorResult = actorRow['Result']

		if actorResult:
			return self.parsePath(actorNameProper, actorResult)

		actorResult = self.baconPyramid.find(actorRow['ActorId'], useCaching)

		if actorResult:
			return self.parsePath(actorNameProper, actorResult)

		return self.showUnsolvableResult(actorNameProper)

	def showBestResults(self, actorName, isFemale = False):
		(shehe, shehim) = ('She', 'her') if isFemale else ('He', 'him')

		print('\a\a\a*-._.\' ' + actorName.upper() + ' \'._.-*'
				'\n?!?!?!?!'
				'\n' + shehe + '\'s soooo dreamy...'
				'\nI saw ' + shehim + ' in this coffee shop on Orachard last '
				'Sunday.')

	def showResults(self, actorName, degrees, path):
		loadingComplete(bold(actorName) + ' is ' + bold(str(degrees) + u'\xb0'))

		for degree in path:
			print(degree)

		self.showBenchmark()

	def showBenchmark(self):
		print('Took ' + self.benchmark.end() + '.')

	def showNoResults(self, actorName):
		print('I couldn\'t find ' + bold(actorName) + '.'
			'\nAre you sure that\'s someone in Hollywood? I\'ve never heard of '
			'them.')

	def parsePath(self, actorName, actorResult):
		pathList = self.getPathList(
				actorName,
				actorResult['path'],
				self.getEntityDictionary('Actor', actorResult['actors']),
				self.getEntityDictionary('Film', actorResult['films']),
				)

		self.showResults(actorName, actorResult['baconDegrees'], pathList)

	def getEntityDictionary(self, entityType, searchValues):
		dictionary = {}

		if not len(searchValues):
			return

		searchMethod = 'get' + entityType + 'sById'

		for result in getattr(self.baconSearch, searchMethod)(searchValues):
			dictionary[result[entityType + 'Id']] = result[entityType + 'Name']

		return dictionary

	def getPathList(self, actorName, path, actors, films):
		pathAsActorsAndFilms = self.getPathAsActorsAndFilms(path, actors, films)
		pathAsActorsAndFilms.insert(0, actorName)
		pathAsActorsAndFilms.append('Kevin Bacon')
		pathList = []
		i = 0

		while i < len(pathAsActorsAndFilms) - 2:
			pathList.append(bold(pathAsActorsAndFilms[i]) +
					' was in ' + bold(pathAsActorsAndFilms[i + 1]) +
					' with ' + bold(pathAsActorsAndFilms[i + 2]) + '.')
			i += 2

		return pathList

	def getPathAsActorsAndFilms(self, path, actors, films):
		pathAsActorsAndFilms = []

		for index, entityId in enumerate(path):
			if index % 2 == 0:
				pathAsActorsAndFilms.append(films[entityId])

			else:
				pathAsActorsAndFilms.append(actors[entityId])

		return pathAsActorsAndFilms

	def showUnsolvableResult(self, actorName):
		noConnection = ('Inconceivable! ' + actorName + ' has no connection to '
			'Kevin Bacon.')

		self.showResults(actorName, 'Infinity', [noConnection])

	def complete(self):
		self.prep()
		print('"Wait, wait. I worry what you just heard was, \'Give me a lot '
			'of bacon\'..."')
		self.baconPyramid.find(False, True)
		print('Order\'s up.')
		self.showBenchmark()

	def overwrite(self, tarFileForOverwite):
		self.baconUpdate.overwrite(tarFileForOverwite)