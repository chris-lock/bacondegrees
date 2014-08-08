#!/usr/bin/env python

from baconsearch import BaconSearch
from copy import deepcopy, copy
from baconhelpers import printAndExit, loading
import gc

## Builds a pyramid of all the nodes with their connection to Kevin. The 
#  approach is to add alternating tiers of actors and films starting at Kevin
#  and filtering the ones we've already found until there are none left. Solving
#  starting at Kevin allows us to have solved any actor found on the way and 
#  store the pyramid for future look ups so we don't have to start over. The
#  results is a dictionary that include the actor and film ids in the path to 
#  the node and the path of ids. We can exclude the two en points since we know
#  where we're starting and finishing.
#
#  @author Chris Lock
class BaconPyramid():
	# @constant The no results string used.
	NO_RESULTS = '__NO_RESULT__'

	# @type {object} An instance of the search object
	baconSearch = BaconSearch()
	# @type {int} The actor id we're looking for.
	actorId = 0
	# @type {bool} Should we cache results
	useCaching = False
	# @type {dictionary} The pyramid including actors, films, the completed 
	#	tier, and the pyramid
	pyramid = {}
	# @type {tuples} All the actor ids found so far
	actors = ()
	# @type {tuples} All the film ids found so far
	films = ()
	# @type {list} All the tiers
	tiers = []
	# @type {dictionary} The current tier
	tier = {}
	# @type {int} The current tier index
	tierIndex = 0
	# @type {bool} Is the current tier complete
	tierIsComplete = False
	# @type {int} The pointer in the current tier
	pointer = 0
	# @type {list} The nodes on the current tier
	nodes = []
	# @type {int} The current node index
	nodeId = 0
	# @type {bool} Have we found the actor
	actorNodeFound = None
	# @type {tuple} All the paths to actors to cache
	paths = ()
	# @type {int} How many itterations we've been through
	itterations = 0

	## An empty constructor.
	#
	#  @param {object} self The object
	#  @return void
	def __init__(self):
		pass

	## Checks to see if we already have a cached pyramid. Sets pyramid 
	#  properties as attributes for easier reference. Then tries to find the
	#  result catching any keyboard interruptions.
	#
	#  @param {object} self The object
	#  @param {int} actorId The actor id we're looking for
	#  @param {bool} useCaching Should we cache the state of the tree and found
	#		actors
	#  @return void
	def find(self, actorId, useCaching):
		gc.collect()

		oldPyramid = self.baconSearch.getBaconPyramid()

		self.actorId = actorId
		self.useCaching = useCaching
		self.pyramid = oldPyramid if oldPyramid else self.getTip()
		self.actors = self.pyramid['actors']
		self.films = self.pyramid['films']
		self.tiers = self.pyramid['tiers']
		self.tierIndex = self.pyramid['complete'] + 1

		try:
			return self.findActorPyramid()

		except KeyboardInterrupt:
			printAndExit('\nPatience...')

	## Gets a new tip for the pyramid.
	#
	#  @param {object} self The object
	#  @return {dictionary} The pyramid dictionary
	def getTip(self):
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

	## Gets a new tier for the pyramid.
	#
	#  @param {object} self The object
	#  @param {bool} isActors Is this an actor tier
	#  @param {list} nodes The nodes on the tier
	#  @return {dictionary} The tier dictionary
	def getNewTier(self, isActors = True, nodes = []):
		return deepcopy({
			'isActors': isActors,
			'pointer': 0,
			'nodes': nodes,
			})

	## Gets a new node for the pyramid.
	#
	#  @param {object} self The object
	#  @param {int} id The id of the actor of film
	#  @param {mixed} parentNode The index of the parent node if one
	#  @return {tuple} The node tuple
	def getNewNode(self, id, parentNode = False):
		return copy((id, parentNode))

	## Looks itteratively for the actor id in the pyramid and does garbage
	#  collection on each loop.
	#
	#  @param {object} self The object
	#  @return void
	def findActorPyramid(self):
		result = None

		while not result:
			result = self.getNextOpenTier()
			gc.collect()

		self.updatePyramidAndActorPaths()

		return result if not result == self.NO_RESULTS else None

	## Finds the next unsolved tier and determines if it's a actor or film tier.
	#
	#  @param {object} self The object
	#  @return {mixed} None if we need to keep going. No result if we've 
	#		finished. Or the actor dictionary.
	def getNextOpenTier(self):
		if self.tierIndex >= len(self.tiers):
			return self.NO_RESULTS

		if self.tiers[self.tierIndex]['isActors']:
			return self.updateActorTier()

		else:
			return self.updateFilmTier()

	## Adds films to the next tier for the actors in the current tier. For the
	#  films of each actor, we check the casts for the actor so we don't have
	#  uneccessary films in the pyramid. Once we've comleted the tier, we go to
	#  the next actor tier. On the last tiers, we may not have another actor
	#  tier until we've checked a few films.
	#
	#  @param {object} self The object
	#  @return {mixed} None if we need to keep going. No result if we've 
	#		finished since we can't find an actor when adding films.
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

	## We can only set complete tiers for actor tiers, since film tiers are
	#  filled and complete repeatedly.
	#
	#  @param {object} self The object
	#  @return void
	def updateTiersComplete(self):
		self.pyramid['complete'] = self.tierIndex

	## Sets all the properties for the current tier.
	#
	#  @param {object} self The object
	#  @return void
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

	## Checks to see if there's another actor tier. If not, we're finished
	#
	#  @param {object} self The object
	#  @return {mixed} None if we need to keep going. No result if we've 
	#		finished since we can't find an actor when adding films.
	def updateActorTierOrFinish(self):
		if self.tierIndex >= len(self.tiers):
			self.updateTiersComplete()

			return self.NO_RESULTS

		return self.updateActorTier()

	## Adds a film to the next tier and the tuple of found films.
	#
	#  @param {object} self The object
	#  @param {int} filmId The id for the film
	#  @param {int} newTierIndex The new tier index
	#  @return void
	def addFilmToTier(self, filmId, newTierIndex):
		self.itterate()

		if filmId not in self.films:
			self.films += (filmId, )
			self.addNodeToTier(newTierIndex, filmId, self.pointer, False)

	## Prints a updating loading icon for each itteration.
	#
	#  @param {object} self The object
	#  @return void
	def itterate(self):
		self.itterations += 1
		loading(self.itterations)

	## Checks to see if the tier already exists. If not, creates it, then, adds
	#  the node to it
	#
	#  @param {object} self The object
	#  @param {object} newTierIndex The index for the tier
	#  @param {object} nodeId The id of the entity to add
	#  @param {object} nodeParentIndex The index of the parent node
	#  @param {object} isActors If the new tier is an actors tier
	#  @return void
	def addNodeToTier(self, newTierIndex, nodeId, nodeParentIndex, isActors):
		if len(self.tiers) <= newTierIndex:
			self.tiers.append(self.getNewTier(isActors))

		node = self.getNewNode(nodeId, nodeParentIndex)
		self.tiers[newTierIndex]['nodes'].append(node)

		return node

	## Updates the pointer one index.
	#
	#  @param {object} self The object
	#  @return void
	def setPointer(self):
		self.tier['pointer'] = self.pointer + 1

	## Adds actors to the next tier for the films in the current tier. If we
	#  find the actor, we add his fellow cast members since we've already found
	#  them. If we don't find it, we go back to the previous film tier so it
	#  can add more actors or move uus forward.
	#
	#  @param {object} self The object
	#  @return {mixed} None if we need to keep going. No result if we've 
	#		finished. Or the actor dictionary.
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

	## Gets the dictionary for the path to the current move since it will be the
	#  same for all cast members since we don't store their id.
	#
	#  @param {object} self The object
	#  @param {object} nodeParentIndex The index of the parent node
	#  @param {object} tierIndex The index of the tier
	#  @return {dictionary} The results dictionary for all cast members since
	#		don't include their id
	def getResultForCast(self, nodeParentIndex, tierIndex):
		if not self.useCaching:
			return

		startingNode = self.getNewNode(0, nodeParentIndex)

		return self.getActorResult(startingNode, tierIndex)

	## Adds a actor to the next tier, the tuple of found actors, and set of 
	#  results to cache
	#
	#  @param {object} self The object
	#  @param {int} actorId The id for the actor
	#  @param {int} newTierIndex The new tier index
	#  @param {dictionary} resultForCast The path to the film
	#  @return void
	def addActorToTier(self, actorId, newTierIndex, resultForCast):
		self.itterate()

		if actorId not in self.actors:
			self.actors += (actorId, )
			node = self.addNodeToTier(newTierIndex, actorId, self.pointer, True)
			self.addActorResult(actorId, resultForCast)

			if actorId == self.actorId:
				self.actorNodeFound = node

	## Adds a tuple to the set of results to cache.
	#
	#  @param {object} self The object
	#  @param {int} actorId The id for the actor
	#  @param {dictionary} resultForCast The path to the film
	#  @return void
	def addActorResult(self, actorId, resultForCast):
		if self.useCaching:
			baconDegrees = resultForCast['baconDegrees']
			self.paths += ((resultForCast, baconDegrees, actorId,),)

	## Gets the dictionary of path to the actor by recursively getting each
	#  nodes parent node until none if left.
	#
	#  @param {object} self The object
	#  @param {tuple} node The tuple of the starting node
	#  @param {int} tierIndex The tier we're starting at
	#  @param {tuple} path The ids that lead from the actor to Kevin
	#  @param {dictionary} resultForCast The path to the film
	#  @return void
	def getActorResult(self, node, tierIndex, path = ()):
		if tierIndex == 0:
			return self.getActorResultDictionary(path)

		parentNodeIndex = node[1]
		parentNode = self.tiers[tierIndex]['nodes'][parentNodeIndex]
		path += (parentNode[0],)

		return self.getActorResult(parentNode, tierIndex - 1, path)

	## Gets the dictionary of path to the actor based on every other id being a
	#  actor if then a film id.
	#
	#  @param {object} self The object
	#  @param {tuple} path The ids that lead from the actor to Kevin
	#  @param {dictionary} resultForCast The path to the film
	#  @return void
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

	## Saves the current state of the pyramid and all the found actors to the
	#  database.
	#
	#  @param {object} self The object
	#  @return void
	def updatePyramidAndActorPaths(self):
		if self.useCaching:
			self.pyramid['actors'] = self.actors
			self.pyramid['films'] = self.films

			self.baconSearch.updateBaconPyramid(self.pyramid)
			self.baconSearch.updateActorResults(self.paths)

	## Solves the entire pyrmaid by looking for a non-existent actor id.
	#
	#  @param {object} self The object
	#  @return void
	def findAll(self):
		self.find(False, True)