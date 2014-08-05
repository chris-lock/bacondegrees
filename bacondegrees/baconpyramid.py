from baconsearch import BaconSearch
import sys
from copy import deepcopy
from baconhelpers import printAndExit, loading

class BaconPyramid():
	baconSearch = BaconSearch()
	actorId = 0
	useCaching = False
	pyramid = {}
	actors = ()
	films = ()
	tiers = []
	tier = {}
	tierIsComplete = False
	pointer = 0
	nodes = []
	nodeId = 0
	actorNodeFound = None
	paths = ()
	itterations = 0

	def __init__(self):
		pass

	def find(self, actorId, useCaching):
		sys.setrecursionlimit(999999999)
		# oldPyramid = self.baconSearch.getBaconPyramid()

		self.actorId = actorId
		self.useCaching = useCaching
		# self.pyramid = oldPyramid if oldPyramid else self.getRoot()
		self.pyramid = self.getRoot()
		self.actors = self.pyramid['actors']
		self.films = self.pyramid['films']
		self.tiers = self.pyramid['tiers']

		try:
			return self.getNextOpenTier()

		except:
			printAndExit('\nPatience...')

	def getRoot(self):
		baconActorId = self.baconSearch.getBaconActorId()
		tiers = [
			self.getNewTier(True, [self.getNewNode(baconActorId)])
			]

		return {
			'actors': (baconActorId, ),
			'films': (),
			'tiers': tiers,
			'complete': -1,
			}

	def getNewTier(self, isActors = True, nodes = []):
		return deepcopy({
			'isActors': isActors,
			'pointer': 0,
			'nodes': nodes,
			})

	def getNewNode(self, id, parentNode = False):
		return deepcopy({
			'id': id,
			'parentNode': parentNode,
			})

	def getNextOpenTier(self):
		openTierIndex = self.pyramid['complete'] + 1

		if openTierIndex >= len(self.tiers):
			return None

		if self.tiers[openTierIndex]['isActors']:
			return self.updateActorTier(openTierIndex)

		else:
			return self.updateFilmTier(openTierIndex)

	def updateActorTier(self, tierIndex):
		self.setTier(tierIndex)

		if self.tierIsComplete:
			return self.updateActorTierOrFinish(tierIndex + 2)

		for film in self.baconSearch.getFilmsByActorId(self.nodeId):
			self.addFilmToTier(film['FilmId'], tierIndex + 1)

		self.setPointer()

		return self.updateFilmTier(tierIndex + 1)

	def setTier(self, tierIndex):
		self.tier = self.tiers[tierIndex]
		self.pointer = self.tier['pointer']
		self.nodes = self.tier['nodes']

		if self.pointer < len(self.nodes):
			self.tierIsComplete = False
			self.nodeId = self.nodes[self.pointer]['id']

		else:
			self.tierIsComplete = True
			self.nodeId = 0

	def updateActorTierOrFinish(self, newTierIndex):
		if newTierIndex > len(self.tiers):
			print('Here')
			self.cacheState()
			return None

		return self.updateActorTier(newTierIndex)

	def addFilmToTier(self, filmId, newTierIndex):
		self.itterate()

		if filmId not in self.films:
			self.films += (filmId, )
			self.addNodeToTier(newTierIndex, filmId, self.pointer, False)

	def itterate(self):
		self.itterations += 1
		loading(self.itterations)

	def addNodeToTier(self, newTierIndex, nodeId, nodeParentIndex, isActors):
		if len(self.tiers) <= newTierIndex:
			self.tiers.append(self.getNewTier(isActors))

		node = self.getNewNode(nodeId, nodeParentIndex)
		self.tiers[newTierIndex]['nodes'].append(node)

		return node

	def setPointer(self):
		self.tier['pointer'] = self.pointer + 1

	def updateFilmTier(self, tierIndex):
		self.setTier(tierIndex)

		if self.tierIsComplete:
			return self.updateActorTier(tierIndex - 1)

		resultForCast = self.getResultForCast(self.pointer, tierIndex)

		for actor in self.baconSearch.getActorsByFilmId(self.nodeId):
			self.addActorToTier(actor['ActorId'], tierIndex + 1, resultForCast)

		self.setPointer()

		if not self.actorNodeFound:
			return self.updateFilmTier(tierIndex)

		self.cacheState()

		return self.getActorResult(self.actorNodeFound, tierIndex)

	def getResultForCast(self, nodeParentIndex, tierIndex):
		if not self.useCaching:
			return

		startingNode = self.getNewNode(0, nodeParentIndex)

		return self.getActorResult(startingNode, tierIndex)

	def addActorToTier(self, actorId, newTierIndex, resultForCast):
		self.itterate()

		if actorId not in self.actors:
			self.actors += (actorId, )
			node = self.addNodeToTier(newTierIndex, actorId, self.pointer, True)
			self.addActorResult(actorId, resultForCast)

			if actorId == self.actorId:
				self.actorNodeFound = node

	def addActorResult(self, actorId, resultForCast):
		if self.useCaching:
			baconDegrees = resultForCast['baconDegrees']
			self.paths += ((resultForCast, baconDegrees, actorId,),)

	def getActorResult(self, node, tierIndex, path = ()):
		if tierIndex == 0:
			return self.getActorResultDictionary(path)

		parentNodeIndex = node['parentNode']
		parentNode = self.tiers[tierIndex]['nodes'][parentNodeIndex]
		path += (parentNode['id'],)

		return self.getActorResult(parentNode, tierIndex - 1, path)

	def getActorResultDictionary(self, path):
		pathDictionary = {
			'actors': (),
			'films': (),
			'path': path,
			'baconDegrees': (len(path) + 1) / 2
			}

		for index, node in enumerate(path):
			if index % 2 == 0:
				pathDictionary['films'] += (node,)

			else:
				pathDictionary['actors'] += (node,)

		return pathDictionary

	def cacheState(self):
		if self.useCaching:
			#self.baconSearch.updateBaconPyramid(self.pyramid)
			self.baconSearch.updateActorResults(self.paths)
			self.baconSearch.updateFilmsInPyramid(self.films)