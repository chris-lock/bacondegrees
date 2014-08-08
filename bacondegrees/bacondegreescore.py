#!/usr/bin/env python

from baconsearch import BaconSearch
from baconupdate import BaconUpdate
from baconpyramid import BaconPyramid
from baconhelpers import Benchmark, bold, loadingComplete

## The controller for the module.
#
#  @author Chris Lock
class BaconDegreesCore():
	# @type {object} An instance of the search object
	__baconSearch = BaconSearch()
	# @type {object} An instance of the update object
	__baconUpdate = BaconUpdate()
	# @type {object} An instance of the pyramid builder object
	__baconPyramid = BaconPyramid()
	# @type {object} An instance of the benchmark object
	__benchmark = Benchmark()

	## An empty constructor
	#
	#  @param {object} self The object
	#  @return void
	def __init__(self):
		pass

	## The controller for the module.
	#
	#  @param {object} self The object
	#  @param {args} *args All the arguments passed to prep
	#  @return void
	def prep(self, *args):
		self.__baconUpdate.prep(*args)

	## Updates the data with a tar file.
	#
	#  @param {object} self The object
	#  @param {string} tarFileForUpdate the aboslute path to the tar file
	#  @return void
	def update(self, tarFileForUpdate):
		self.__baconUpdate.update(tarFileForUpdate)

	## Preps the data if that hasn't been done yet and starts the benchmark
	#  Show an easter egg if you look me up. If you search for Kevin Bacon, we
	#  don't need to look anything up, othewise, we need to check that the 
	#  search is an actor in the data, then check if we've already solved 
	#  them, if not we run it through the pyramid to get the path. If we don't 
	#  find a result, we call that method, otherwise we print the result.
	#
	#  @param {object} self The object
	#  @param {string} actorName The actor name to look up
	#  @param {bool} useCaching Whether to cache what the result and actors
	#		found along the way
	#  @return void
	def get(self, actorName, useCaching = False):
		self.prep()
		self.__benchmark.start()

		# Easter egg
		if (actorName == 'Chris Lock'):
			return self.__showBestResults(actorName)

		# Kevin Bacon
		if (actorName == 'Kevin Bacon'):
			return self.__showResults(actorName, 0, ['He is himself.'])

		self.__baconSearch.setup().start()
		actorRow = self.__baconSearch.getActorByName(actorName)
		self.__baconSearch.end()

		# Actor no in the data
		if not actorRow:
			return self.__showNoResults(actorName)

		actorNameProper = actorRow['ActorName']
		actorResult = actorRow['Result']

		# Actor already cached
		if actorResult:
			return self.__parsePath(actorNameProper, actorResult)

		actorResult = self.__baconPyramid.find(actorRow['ActorId'], useCaching)

		# Actor found
		if actorResult:
			return self.__parsePath(actorNameProper, actorResult)

		# Actor not solveable
		return self.__showUnsolvableResult(actorNameProper)

	## Prints the easter egg response.
	#
	#  @param {object} self The object
	#  @param {string} actorName The actor name to look up
	#  @param {bool} isFemale Is the actor female
	#  @return void
	def __showBestResults(self, actorName, isFemale = False):
		(shehe, shehim) = ('She', 'her') if isFemale else ('He', 'him')

		print('\a\a\a*-._.\' ' + actorName.upper() + ' \'._.-*'
				'\n?!?!?!?!'
				'\n' + shehe + '\'s soooo dreamy...'
				'\nI saw ' + shehim + ' in this coffee shop on Orachard last '
				'Sunday.')

	## Prints the resulting degrees and the path to get there.
	#
	#  @param {object} self The object
	#  @param {string} actorName The actor name that was solved
	#  @param {string} degrees The degrees of Kevin Bacon
	#  @param {list} path The list of paths to get to Kevin Bacon
	#  @return void
	def __showResults(self, actorName, degrees, path):
		loadingComplete(bold(actorName) + ' is ' + bold(str(degrees) + u'\xb0'))

		for degree in path:
			print(degree)

		self.__showBenchmark()

	## Prints the becnhmark.
	#
	#  @param {object} self The object
	#  @return void
	def __showBenchmark(self):
		print('Took ' + self.__benchmark.end() + '.')

	## Prints the no results message.
	#
	#  @param {object} self The object
	#  @param {string} actorName The actor name that was not solved
	#  @return void
	def __showNoResults(self, actorName):
		print('I couldn\'t find ' + bold(actorName) + '.'
			'\nAre you sure that\'s someone in Hollywood? I\'ve never heard of '
			'them.')

	## Parses the dictionary returned by the pyramid. Gets the names that
	#  correspond with the id's and returns a list with each path.
	#
	#  @param {object} self The object
	#  @param {string} actorName The actor name that was solved
	#  @param {dictionary} actorResult The dictionary returned by the pyramid
	#  @return void
	def __parsePath(self, actorName, actorResult):
		pathList = self.__getPathList(
				actorName,
				actorResult['path'],
				self.__getEntityDictionary('Actor', actorResult['actors']),
				self.__getEntityDictionary('Film', actorResult['films']),
				)

		self.__showResults(actorName, actorResult['baconDegrees'], pathList)

	## Gets a dictionary of ids to names for actors or films.
	#
	#  @param {object} self The object
	#  @param {string} entityType Is this films or actors
	#  @param {tuple} searchValues The tuple containing the ids
	#  @return {dictionary} A dictionary of ids to names
	def __getEntityDictionary(self, entityType, searchValues):
		dictionary = {}

		if not len(searchValues):
			return

		searchMethod = 'get' + entityType + 'sById'

		for result in getattr(self.__baconSearch, searchMethod)(searchValues):
			dictionary[result[entityType + 'Id']] = result[entityType + 'Name']

		return dictionary

	## Takes the path to Kevin and a dictionary of actors and films to map each
	#  id to the node in the path and build a list of each connection.
	#
	#  @param {object} self The object
	#  @param {string} actorName The actor name that was solved
	#  @param {tuple} path The tuple of ids to get to Kevin
	#  @param {dictionary} actors The dictionary of actor ids to names
	#  @param {dictionary} films The dictionary of film ids to names
	#  @return {list} A list of connections, actor was in movie with actor
	def __getPathList(self, actorName, path, actors, films):
		pathAsActorsAndFilms = self.__getPathAsActorsAndFilms(path, actors, 
				films)
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

	## Takes the path to Kevin and a dictionary of actors and films to produce
	#  a tuple of just names.
	#
	#  @param {object} self The object
	#  @param {tuple} path The tuple of ids to get to Kevin
	#  @param {dictionary} actors The dictionary of actor ids to names
	#  @param {dictionary} films The dictionary of film ids to names
	#  @return {tuple} The path to Kevin Bacon as names
	def __getPathAsActorsAndFilms(self, path, actors, films):
		pathAsActorsAndFilms = []

		for index, entityId in enumerate(path):
			if index % 2 == 0:
				pathAsActorsAndFilms.append(films[entityId])

			else:
				pathAsActorsAndFilms.append(actors[entityId])

		return pathAsActorsAndFilms

	## Prints the result for names that have no path to Kevin.
	#
	#  @param {object} self The object
	#  @param {string} actorName The actor name that was unsolveable
	#  @return void
	def __showUnsolvableResult(self, actorName):
		noConnection = ('Inconceivable! ' + actorName + ' has no connection to '
			'Kevin Bacon.')

		self.__showResults(actorName, 'Infinity', [noConnection])

	## Preps the data if it hasn't been done, starts the becnhmark, completes 
	#  the entire tree from Kevin, and prints the benchmark.
	#
	#  @param {object} self The object
	#  @return void
	def complete(self):
		self.prep()
		print('"Wait, wait. I worry what you just heard was, \'Give me a lot '
			'of bacon\'..."')
		self.__benchmark.start()
		self.__baconPyramid.findAll()
		print('\nOrder\'s up.')
		self.__showBenchmark()

	## Updates the data with a new tar file
	#
	#  @param {object} self The object
	#  @param {string} tarFileForOverwite the aboslute path to the tar file
	#  @return void
	def overwrite(self, tarFileForOverwite):
		self.__baconUpdate.overwrite(tarFileForOverwite)

	## Preps the data if it hasn't been done, starts the becnhmark, completes 
	#  the entire tree from Kevin, finds any actros with no connection to 
	#  Kevin, and prints the benchmark.
	#
	#  @param {object} self The object
	#  @return void
	def getExceptions(self):
		self.prep()
		self.__benchmark.start()
		self.__baconPyramid.findAll()

		for film, actors in self.__baconSearch.getUnsolved().items():
			print(bold(film))

			for actor in actors:
				print(actor)

		self.__showBenchmark()