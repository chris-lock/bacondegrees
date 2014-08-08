#!/usr/bin/env python

import os
from baconsearch import BaconSearch
from baconhelpers import Benchmark, alertAndExit, bold, progressBar
import tarfile
import json

## A class for update the data with a tar.gz contaontaining json files 
#  formatted film.name, cast[].name.
#
#  @author Chris Lock
class BaconUpdate():
	# @type {string} The absolute path to the directory that this file lives in
	__directory = os.path.dirname(os.path.realpath(__file__))
	# @type {string} The default tar file containing json files with films
	__defaultTarFile = __directory + '/films.tar.gz'
	# @type {object} An instance of the search object
	__baconSearch = BaconSearch()
	# @type {object} An instance of the benchmark object
	__benchmark = Benchmark()

	## An empty constructor.
	#
	#  @param {object} self The object
	#  @return void
	def __init__(self):
		pass

	## Creates the data with the tar file.
	#
	#  @param {object} self The object
	#  @param {bool} verbose Should we print if a database has already be
	#  @return void
	def prep(self, verbose = False):
		if self.__hasDefaultTarFile():
			self.update(self.__defaultTarFile, True)
		elif verbose:
			print('Your bacon is already cooked.')

	## Checks if we still have the default tar file.
	#
	#  @param {object} self The object
	#  @return {bool} Whether we still have the file
	def __hasDefaultTarFile(self):
		return os.path.isfile(self.__defaultTarFile)

	## Starts the benchmark, setups the data, starts the connection, and clears
	#  any cached results since they could be inaccurate with new info. We 
	#  check if the file is actually a tar file. We try to upload the file,
	#  catch the keyboard interruption. Then set Kevin Baon's info and delete
	#  the default file.
	#
	#  @param {object} self The object
	#  @param {string} tarFile The path to the tarfile for the update
	#  @return void
	def update(self, tarFile, shouldClean = False):
		self.__benchmark.start()
		self.__baconSearch.setup().start().clearCache()

		if not tarfile.is_tarfile(tarFile):
			alertAndExit(bold(tarFile) + ' is not a tar file.')
		else:
			try:
				self.__uploadTarFile(tarFile)

			except KeyboardInterrupt, SystemExit:
				self.__baconSearch.revert()
				alertAndExit('\nYour bacon is undercooked.')

			self.__setBacon()
			self.__baconSearch.end()

			if shouldClean:
				self.__clean()

	## Opens the tar file. Prints a starting message. Loops through the JSON 
	#  files and adding each film and showing a progress bar based on the total 
	#  number of files. Prints a complete message at the end.
	#
	#  @param {object} self The object
	#  @param {string} tarFile The path to the tarfile for the update
	#  @return void
	def __uploadTarFile(self, tarFileForUpdate):
		itteration = 1

		self.__startProgress()

		with tarfile.open(tarFileForUpdate) as archive:
			jsonFileTotal = len(archive.getmembers())

			for tarinfo in archive:
				if tarinfo.isreg():
					self.__addFileContents(archive.extractfile(tarinfo.name))
					progressBar(itteration, jsonFileTotal)
					itteration += 1

		self.__endProgress()

	## Prints a starting message.
	#
	#  @param {object} self The object
	#  @return void
	def __startProgress(self):
		print('No Bacon? Let\'s cook some.')

	## Adds a film from the json file.
	#
	#  @param {object} self The object
	#  @param {object} jsonFile The json file object
	#  @return void
	def __addFileContents(self, jsonFile):
		(film, cast) = self.__getFilmAndCastFromJsonFile(jsonFile)
		self.__addFilmAndCast(film, cast)

	## Gets the film and cast from the json file.
	#
	#  @param {object} self The object
	#  @param {object} jsonFile The json file object
	#  @return {string} The film name, {list} The cast of the film
	def __getFilmAndCastFromJsonFile(self, jsonFile):
		jsonData = jsonFile.read()
		jsonContent = json.loads(jsonData)
		jsonFile.close()

		return jsonContent['film']['name'], jsonContent['cast']

	## Checks to see if the film is already in the data. If not, we add it and 
	#  get its id. We then look up all the actors in the database. Find the ones
	#  already in there, add the ones not already in there, then add the cast.
	#
	#  @param {object} self The object
	#  @param {string} filmName The film name
	#  @param {list} cast The cast members' names
	#  @return void
	def __addFilmAndCast(self, filmName, cast):
		if not self.__baconSearch.getFilmIdByName(filmName):
			filmId = str(self.__baconSearch.addFilm(filmName))
			actorNames = self.__getActorNamesFromCast(cast)
			castMembers = ()
			actorNamesInSearch = ()
			actorNamesNeeded = ()

			for actorRow in self.__baconSearch.getActorsByName(actorNames):
				castMembers += ((filmId, actorRow['ActorId']),)
				actorNamesInSearch += (actorRow['ActorName'],)

			for actorName in actorNames:
				if actorName not in actorNamesInSearch:
					actorNamesNeeded += (actorName,)

			for actorName in actorNamesNeeded:
				actorId = self.__baconSearch.addActor(actorName)
				castMembers += ((filmId, actorId),)

			self.__baconSearch.addCast(castMembers)

	## Takes the list of actor objects and returns a tuples of names.
	#
	#  @param {object} self The object
	#  @param {list} cast The cast members' objects
	#  @return {tuple} Actors' names
	def __getActorNamesFromCast(self, cast):
		actorNames = ()

		for actor in cast:
			actorNames += (actor['name'],)

		return actorNames

	## Prints the end message with benchmark.
	#
	#  @param {object} self The object
	#  @return void
	def __endProgress(self):
		print(' Took ' + self.__benchmark.end() + '.'
			'\nEnjoy!')

	## Checks to make sure we have Kevin in the data then adds his id.
	#
	#  @param {object} self The object
	#  @return void
	def __setBacon(self):
		baconActorRow = self.__baconSearch.getActorIdByName('Kevin Bacon')

		if not baconActorRow:
			alertAndExit('You\'ve got no bacon! Better find some films '
					'with him in them.')

		self.__baconSearch.updateBaconActorId(baconActorRow['ActorId'])

	## Removes the default tar file.
	#
	#  @param {object} self The object
	#  @return void
	def __clean(self):
		os.remove(self.__defaultTarFile)

	## Clears all the existing data and uploads a new tar file.
	#
	#  @param {object} self The object
	#  @return void
	def overwrite(self, tarFileForOverwite):
		self.__baconSearch.clearAll().setup().start()
		self.update(tarFileForOverwite)
		self.__baconSearch.end()