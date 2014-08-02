import os
import tarfile
import json
from baconsearch import BaconSearch

class BaconTree():
	directory = os.path.dirname(os.path.realpath(__file__))
	defaultTarFile = directory + '/films.tar.gz'
	baconsearch = BaconSearch()

	def __init__(self):
		self.prep()

	def prep(self):
		self.baconsearch.setup().start()
		self.update(self.defaultTarFile)
		self.baconsearch.end()

	def update(self, tarFileForUpdate):
		with tarfile.open(tarFileForUpdate) as archive:
			for tarinfo in archive:
				if tarinfo.isreg():
					self.addFileContents(archive.extractfile(tarinfo.name))
					break

	def addFileContents(self, jsonFile):
		(film, cast) = self.getFilmAndCastFromFile(jsonFile)
		self.addFilmAndCast(film, cast)

	def getFilmAndCastFromFile(self, jsonFile):
		jsonData = jsonFile.read()
		jsonContent = json.loads(jsonData)
		jsonFile.close()

		return jsonContent['film']['name'], jsonContent['cast']

	def addFilmAndCast(self, filmName, cast):
		if not self.baconsearch.getFilmIdByName(filmName):
			filmId = self.baconsearch.addFilm(filmName)

			for actor in cast:
				actorId = self.baconsearch.getActorIdByName(actor['name'])

				if not actorId:
					actorId = self.baconsearch.addActor(actor['name'])

				self.baconsearch.addCastMember(filmId, actorId)

	def get(self, actorName, useCaching = False):
		return

	def complete(self):
		print('Wait, wait. I worry what you just heard was, "Give me a lot of '
			'bacon"...')

	def getExceptions(self):
		self.complete()
		print('Veggies')

	def overwrite(self, tarFileForOverwite):
		self.baconsearch.start().dropAllEntries()
		self.update(tarFileForOverwite)
		self.baconsearch.end()