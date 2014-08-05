from baconsearch import BaconSearch
from copy import deepcopy

import sys
import pprint
pp = pprint.PrettyPrinter(indent=4)

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

	def __init__(self):
		pass

	def find(self, actorId, useCaching):
		#oldPyramid = self.baconSearch.getBaconPyramid()

		self.actorId = actorId
		self.useCaching = useCaching
		#self.pyramid = oldPyramid if oldPyramid else self.getRoot()
		self.pyramid = self.getRoot()
		self.actors = self.pyramid['actors']
		self.films = self.pyramid['films']
		self.tiers = self.pyramid['tiers']

		return self.getNextOpenTier()

	def getRoot(self):
		baconActorId = self.baconSearch.getBaconActorId()
		tiers = [
			self.getNewTier(True, [self.getNewNode(baconActorId)])
			]

		return {
			'actors': (baconActorId, ),
			'films': (),
			'tiers': tiers,
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
		startingTier = None

		for index, tier in enumerate(self.tiers):
			if not tier['pointer'] == len(tier['nodes']):
				startingTier = index

		if startingTier == None:
			return None

		return self.updateActorTier(startingTier)

	def updateActorTier(self, tierIndex):
		self.setTier(tierIndex)

		if self.tierIsComplete:
			return self.updateActorTier(tierIndex + 2)

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

	def addFilmToTier(self, filmId, newTierIndex):
		if filmId not in self.films:
			self.films += (filmId, )
			self.addNodeToTier(newTierIndex, filmId, self.pointer, False)

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

		pathToFilm = self.getPathToFilm(self.pointer, tierIndex)

		for actor in self.baconSearch.getActorsByFilmId(self.nodeId):
			self.addActorToTier(actor['ActorId'], tierIndex + 1, pathToFilm)

		self.setPointer()

		if not self.actorNodeFound:
			return self.updateFilmTier(tierIndex)

		self.cacheState()

		return self.getPathForNode(self.actorNodeFound, tierIndex)

	def getPathToFilm(self, nodeParentIndex, tierIndex):
		if not self.useCaching:
			return

		startingNode = self.getNewNode(0, nodeParentIndex)

		return self.getPathForNode(startingNode, tierIndex)

	def addActorToTier(self, actorId, newTierIndex, pathToFilm):
		if actorId not in self.actors:
			self.actors += (actorId, )
			node = self.addNodeToTier(newTierIndex, actorId, self.pointer, True)
			self.addActorPath(actorId, pathToFilm)

			if actorId == self.actorId:
				self.actorNodeFound = node

	def addActorPath(self, actorId, pathToFilm):
		if self.useCaching:
			self.paths += ((pathToFilm, actorId,),)

	def getPathForNode(self, node, tierIndex, path = ()):
		if tierIndex == 0:
			return self.getPathDictionary(path)

		parentNodeIndex = node['parentNode']
		parentNode = self.tiers[tierIndex]['nodes'][parentNodeIndex]
		path += (parentNode['id'],)

		return self.getPathForNode(parentNode, tierIndex - 1, path)

	def getPathDictionary(self, path):
		pathDictionary = {
			'actors': (),
			'films': (),
			'path': path,
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
			self.baconSearch.updateActorPaths(self.paths)
			self.baconSearch.updateFilmsInPyramid(self.films)