from baconsearch import BaconSearch
from copy import deepcopy, copy
from baconhelpers import printAndExit, loading
import gc

import sys
import pprint
pp  = pprint.PrettyPrinter(indent=2)

class BaconPyramid():
	noResult = '__NO_RESULT__'
	baconSearch = BaconSearch()
	actorId = 0
	useCaching = False
	pyramid = {}
	actors = ()
	films = ()
	tiers = []
	tier = {}
	tierIndex = 0
	tierIsComplete = False
	pointer = 0
	nodes = []
	nodeId = 0
	actorNodeFound = None
	paths = ()
	itterations = 0
	actorsTotal = 0

	def __init__(self):
		pass

	def find(self, actorId, useCaching):
		gc.collect()

		oldPyramid = self.baconSearch.getBaconPyramid()

		self.actorId = actorId
		self.useCaching = useCaching
		self.pyramid = oldPyramid if oldPyramid else self.getRoot()
		self.actors = self.pyramid['actors']
		self.films = self.pyramid['films']
		self.tiers = self.pyramid['tiers']
		self.tierIndex = self.pyramid['complete'] + 1
		self.actorsTotal = len(self.actors)

		try:
			return self.findActorPyramid()

		except KeyboardInterrupt:
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
		return copy((id, parentNode))

	def findActorPyramid(self):
		result = None

		while not result:
			result = self.getNextOpenTier()
			gc.collect()

		self.updatePyramidAndActorPaths()

		return result if not result == self.noResult else None

	def getNextOpenTier(self):
		if self.tierIndex >= len(self.tiers):
			return self.noResult

		if self.tiers[self.tierIndex]['isActors']:
			return self.updateActorTier()

		else:
			return self.updateFilmTier()

	def updateActorTier(self):
		self.setTier()

		if self.tierIsComplete:
			self.updateTiersComplete()
			self.tierIndex += 2

			return self.updateActorTierOrFinish()

		for film in self.baconSearch.getFilmsByActorId(self.nodeId):
			self.addFilmToTier(film['FilmId'], self.tierIndex + 1)

		self.setPointer()

		if self.tierIndex + 1 < len(self.tiers):
			self.tierIndex += 1

		return None

	def updateTiersComplete(self):
		self.pyramid['complete'] = self.tierIndex

	def setTier(self):
		self.tier = self.tiers[self.tierIndex]
		self.pointer = self.tier['pointer']
		self.nodes = self.tier['nodes']

		if self.pointer < len(self.nodes):
			self.tierIsComplete = False
			self.nodeId = self.nodes[self.pointer][0]

		else:
			self.updateTiersComplete()
			self.tierIsComplete = True
			self.nodeId = 0

	def updateActorTierOrFinish(self):
		if self.tierIndex >= len(self.tiers):
			self.updateTiersComplete()

			return self.noResult

		return self.updateActorTier()

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

	def updateFilmTier(self):
		self.setTier()

		if self.tierIsComplete:
			self.tierIndex -= 1

			return self.updateActorTier()

		resultForCast = self.getResultForCast(self.pointer, self.tierIndex)

		for actor in self.baconSearch.getActorsByFilmId(self.nodeId):
			self.addActorToTier(actor['ActorId'], self.tierIndex + 1,
					resultForCast)

		self.setPointer()

		if not self.actorNodeFound:
			return None

		return self.getActorResult(self.actorNodeFound, self.tierIndex)

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

		parentNodeIndex = node[1]
		parentNode = self.tiers[tierIndex]['nodes'][parentNodeIndex]
		path += (parentNode[0],)

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

	def updatePyramidAndActorPaths(self):
		if self.useCaching:
			self.pyramid['actors'] = self.actors
			self.pyramid['films'] = self.films

			self.baconSearch.updateBaconPyramid(self.pyramid)
			self.baconSearch.updateActorResults(self.paths)

	def findAll(self):
		self.find(False, True)