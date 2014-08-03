from baconsearch import BaconSearch
from baconupdate import BaconUpdate

class BaconDegreesCore():
	baconSearch = BaconSearch()
	baconUpdate = BaconUpdate()

	def __init__(self):
		pass

	def prep(self):
		self.baconUpdate.prep()

	def update(self, tarFileForUpdate):
		self.baconUpdate.update(tarFileForUpdate)

	def get(self, actorName, useCaching = False):
		self.prep()

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

		return self.getPath(actorName, actorRow['ActorId'], useCaching)

	def showResults(self, actorName, degrees, path):
		print(actorName + ' is ' + str(degrees) + u'\xb0')

		for degree in path:
			print(degree)

	def parsePath(self, path):
		pass

	def getPath(self, actorName, actorId, useCaching):
		print(self.baconSearch.getActorsByFilmId(actorId))

	def showNoResults(self, actorName):
		print('I couldn\'t find \'' + actorName + '\'.')
		print('Are you sure that\'s someone in Hollywood? I\'ve never heard of '
			'them.')

	def complete(self):
		self.prep()
		print('Wait, wait. I worry what you just heard was, "Give me a lot of '
			'bacon"...')

	def overwrite(self, tarFileForOverwite):
		self.prep()
		self.baconUpdate.update(tarFileForOverwite)