#!/usr/bin/env python

#	http://www.ibm.com/developerworks/aix/library/au-pythocli/
#	https://github.com/cakebread/yolk/tree/develop/yolk
#	http://gehrcke.de/2014/02/distributing-a-python-command-line-application/
#	https://github.com/jgehrcke/python-cmdline-bootstrap
#	http://zetcode.com/db/sqlitepythontutorial/

import os
import sqlite3
import sys

class BaconSearch():
	directory = os.path.dirname(os.path.realpath(__file__))
	database = None
	databasePath = directory + '/baconsearch-data.db'
	databaseTables = {
		'Bacon': 'Tree TEXT',
		'Actors': 'ActorId INTEGER PRIMARY KEY, ActorName TEXT, Path TEXT',
		'Films': 'FilmId INTEGER PRIMARY KEY, FilmName TEXT, InTree INT',
		'Casts': 'FilmId INT, ActorId INT',
		}
	cursor = None

	def __init__(self):
		self.setup()

	def setup(self):
		if not self.hasDatabase():
			self.start().createDatabaseTables().end()

		return self

	def hasDatabase(self):
		return os.path.isfile(self.databasePath)

	def start(self):
		if self.database:
			return self

		try:
			self.database = sqlite3.connect(self.databasePath)
			self.cursor = self.database.cursor()

			return self

		except sqlite3.Error, error:
			print('Error %s:' % error.args[0])
			sys.exit(1)

	def createDatabaseTables(self):
		for (tableName, columns) in self.databaseTables.items():
			create = ('CREATE TABLE IF NOT EXISTS ' + tableName +
				'(' + columns + ')')
			self.getCursor().execute(create)

		return self

	def getCursor(self):
		if not self.cursor:
			self.start()

		return self.cursor

	def end(self):
		self.commit()

		if self.database:
			self.database.close()
			self.database = None
			self.cursor = None

	def commit(self):
		if self.database:
			self.database.commit()

		return self

	def getFilmIdByName(self, filmName):
		return self.getItemIdByName('Film', filmName)

	def getItemIdByName(self, itemType, itemName):
		selectColumn = itemType + 'Id'
		whereColumn = itemType + 'Name'

		return self.getItem(itemType, selectColumn, whereColumn, itemName)

	def getItem(self, itemType, selectColumn, whereColumn, whereValue):
		query = ('SELECT ' + selectColumn + ' FROM ' + itemType + 's '
			'WHERE ' + whereColumn + ' = "' + whereValue + '"')

		return self.getCursor().execute(query).fetchone()

	def getActorIdByName(self, actorName):
		return self.getItemIdByName('Actor', actorName)

	def addFilm(self, filmName):
		return self.addItem('Film', filmName)

	def addItem(self, itemType, itemNameValue):
		return self.insertRow('INSERT INTO ' + itemType + 's '
			'(' + itemType + 'Name) VALUES ("' + itemNameValue + '")')

	def insertRow(self, insert):
		self.getCursor().execute(insert)
		self.commit()

		return self.getCursor().lastrowid

	def addActor(self, actorName):
		return self.addItem('Actor', actorName)

	def addCastMember(self, filmId, actorId):
		return self.insertRow('INSERT INTO Casts (FilmId, ActorId) '
			'VALUES ("' + str(filmId) + '", "' + str(actorId) + '")')

	def dropAllRows(self):
		print('NO!!!!')