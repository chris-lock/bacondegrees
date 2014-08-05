import os
from baconsearch import BaconSearch
import tarfile
import json
import sys
from time import time

class BaconUpdate():
	directory = os.path.dirname(os.path.realpath(__file__))
	defaultTarFile = directory + '/films.tar.gz'
	baconSearch = BaconSearch()
	time = None

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
		self.time = time()
		self.baconSearch.setup().start()

		if not tarfile.is_tarfile(tarFile):
			self.showAndExit('\'' + tarFile + '\' is not a tar file.')
		else:
			try:
				self.uploadTarFile(tarFile)

			except (KeyboardInterrupt, SystemExit):
				self.baconSearch.revert()
				self.showExitWarning()

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
					self.updateProgress(itteration, jsonFileTotal)
					itteration += 1

		self.endProgress()

	def startProgress(self):
		print('No Bacon? Let\'s cook some.\nSizzle...')
		sys.stdout.flush()

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

	def updateProgress(self, itteration, jsonFileTotal):
		progressBar = self.getProgressBar(itteration, jsonFileTotal)
		jsonFileProgress = '(' + str(itteration) + '/' + str(jsonFileTotal) + ')'

		sys.stdout.write('\r' + progressBar + ' ' + jsonFileProgress)
		sys.stdout.flush()

	def getProgressBar(self, current, total):
		steps = 19.0
		progress = int(float(current) / float(total) * steps)
		progressRemaining = int(steps) - progress

		return '[~' + ('~' * progress) + (' ' * progressRemaining) + ']'

	def endProgress(self):
		print(' Took ' + self.getBenchmark() + '.'
			'\nEnjoy!')

	def getBenchmark(self):
		secondsRaw = time() - self.time
		minutes, seconds = divmod(secondsRaw, 60)
		hours, minutes = divmod(minutes, 60)
		benchmark = self.getPlural(seconds, 'second')

		if minutes:
			endCharacter = ', and ' if hours else ' and '
			benchmark = (self.getPlural(int(minutes), 'minute', endCharacter) +
					benchmark)
		else:
			return benchmark

		if hours:
			benchmark = self.getPlural(int(hours), 'hour', ', ') + benchmark

		return benchmark

	def getPlural(self, value, measurement, endCharacter = ''):
		plural = '' if value == 1 else 's'

		return str(value) + ' ' + measurement + plural + endCharacter

	def showExitWarning(self):
		self.showAndExit('\nYour bacon is undercooked.')

	def showAndExit(self, message):
		print('\a' + message)
		sys.exit(1)

	def setBacon(self):
		baconActorRow = self.baconSearch.getActorIdByName('Kevin Bacon')

		if not baconActorRow:
			self.showAndExit('You\'ve got no bacon! Better find some films '
					'with him in them.')

		self.baconSearch.updateBaconActorId(baconActorRow['ActorId'])

	def clean(self):
		os.remove(self.defaultTarFile)

	def overwrite(self, tarFileForOverwite):
		self.baconSearch.dropAll().setup().start()
		self.update(tarFileForOverwite)
		self.baconSearch.end()