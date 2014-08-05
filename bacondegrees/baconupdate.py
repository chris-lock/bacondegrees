import os
from baconsearch import BaconSearch
from baconhelpers import Benchmark, printAndExit, bold, progressBar
import tarfile
import json

class BaconUpdate():
	directory = os.path.dirname(os.path.realpath(__file__))
	defaultTarFile = directory + '/films.tar.gz'
	baconSearch = BaconSearch()
	benchmark = Benchmark()

	def __init__(self):
		pass

	def prep(self, verbose = False):
		if self.hasDefaultTarFile():
			self.update(self.defaultTarFile, True)
		elif verbose:
			print('Your bacon is already cooked.')

	def hasDefaultTarFile(self):
		return os.path.isfile(self.defaultTarFile)

	def update(self, tarFile, shouldClean = False):
		self.benchmark.start()
		self.baconSearch.setup().start().clearCache()

		if not tarfile.is_tarfile(tarFile):
			printAndExit(bold(tarFile) + ' is not a tar file.')
		else:
			try:
				self.uploadTarFile(tarFile)

			except (KeyboardInterrupt, SystemExit):
				self.baconSearch.revert()
				printAndExit('\nYour bacon is undercooked.')

			self.setBacon()
			self.baconSearch.end()

			if shouldClean:
				self.clean()

	def uploadTarFile(self, tarFileForUpdate):
		itteration = 1

		self.startProgress()

		with tarfile.open(tarFileForUpdate) as archive:
			jsonFileTotal = len(archive.getmembers())

			for tarinfo in archive:
				if tarinfo.isreg():
					self.addFileContents(archive.extractfile(tarinfo.name))
					progressBar(itteration, jsonFileTotal)
					itteration += 1

		self.endProgress()

	def startProgress(self):
		print('No Bacon? Let\'s cook some.\nSizzle...')

	def addFileContents(self, jsonFile):
		(film, cast) = self.getFilmAndCastFromJsonFile(jsonFile)
		self.addFilmAndCast(film, cast)

	def getFilmAndCastFromJsonFile(self, jsonFile):
		jsonData = jsonFile.read()
		jsonContent = json.loads(jsonData)
		jsonFile.close()

		return jsonContent['film']['name'], jsonContent['cast']

	def addFilmAndCast(self, filmName, cast):
		if not self.baconSearch.getFilmIdByName(filmName):
			filmId = str(self.baconSearch.addFilm(filmName))
			actorNames = self.getActorNamesFromCast(cast)
			castMembers = ()
			actorNamesInSearch = ()
			actorNamesNeeded = ()

			for actorRow in self.baconSearch.getActorsByName(actorNames):
				castMembers += ((filmId, actorRow['ActorId']),)
				actorNamesInSearch += (actorRow['ActorName'],)

			for actorName in actorNames:
				if actorName not in actorNamesInSearch:
					actorNamesNeeded += (actorName,)

			for actorName in actorNamesNeeded:
				actorId = self.baconSearch.addActor(actorName)
				castMembers += ((filmId, actorId),)

			self.baconSearch.addCast(castMembers)

	def getActorNamesFromCast(self, cast):
		actorNames = ()

		for actor in cast:
			actorNames += (actor['name'],)

		return actorNames

	def endProgress(self):
		print(' Took ' + self.benchmark.end() + '.'
			'\nEnjoy!')

	def setBacon(self):
		baconActorRow = self.baconSearch.getActorIdByName('Kevin Bacon')

		if not baconActorRow:
			printAndExit('You\'ve got no bacon! Better find some films '
					'with him in them.')

		self.baconSearch.updateBaconActorId(baconActorRow['ActorId'])

	def clean(self):
		os.remove(self.defaultTarFile)

	def overwrite(self, tarFileForOverwite):
		self.baconSearch.dropAll().setup().start()
		self.update(tarFileForOverwite)
		self.baconSearch.end()