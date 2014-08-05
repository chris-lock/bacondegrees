#!/usr/bin/env python

#	http://www.ibm.com/developerworks/aix/library/au-pythocli/
#	https://github.com/cakebread/yolk/tree/develop/yolk
#	http://gehrcke.de/2014/02/distributing-a-python-command-line-application/
#	https://github.com/jgehrcke/python-cmdline-bootstrap
#	http://zetcode.com/db/sqlitepythontutorial/
#	http://www.darkcoding.net/software/pretty-command-line-console-output-on-unix-in-python-and-go-lang/

import os
import sqlite3
import sys
import pickle

class BaconSearch():
	directory = os.path.dirname(os.path.realpath(__file__))
	connection = None
	databasePath = directory + '/baconsearch.db'
	databaseTables = {
		'Bacon': 'ActorId INT, Pyramid TEXT',
		'Actors': 'ActorId INTEGER PRIMARY KEY, ActorName TEXT, Path TEXT',
		'Films': 'FilmId INTEGER PRIMARY KEY, FilmName TEXT, InPyramid INT',
		'Casts': 'FilmId INT, ActorId INT',
		}
	cursor = None
	baconRowId = 1

	def __init__(self):
		pass

	def setup(self):
		if not self.isSetup():
			self.start().createDatabaseTables().end()

		return self

	def isSetup(self):
		return os.path.isfile(self.databasePath)

	def start(self):
		if self.connection:
			return self

		try:
			self.connection = sqlite3.connect(self.databasePath)
			self.connection.row_factory = sqlite3.Row
			self.cursor = self.connection.cursor()

			return self

		except sqlite3.Error, error:
			print('\aError %s:' % error.args[0])
			sys.exit(1)

	def createDatabaseTables(self):
		for (tableName, columns) in self.databaseTables.items():
			create = ('CREATE TABLE IF NOT EXISTS ' + tableName +
					'(' + columns + ')')
			self.execute(create)

		insert = 'INSERT OR REPLACE INTO Bacon (ROWID, ActorId) VALUES (?, ?)'
		self.execute(insert, (self.baconRowId, 0,))

		return self

	def execute(self, *args):
		return self.getCursor().execute(*args)

	def getCursor(self):
		if not self.cursor:
			self.start()

		return self.cursor

	def end(self):
		self.commit()

		if self.connection:
			self.connection.close()
			self.connection = None
			self.cursor = None

	def commit(self):
		if self.connection:
			self.connection.commit()

		return self

	def getFilmIdByName(self, filmName):
		return self.getEntityIdByName('Film', filmName)

	def getEntityIdByName(self, entityType, entityName):
		select = entityType + 'Id'
		where = entityType + 'Name'

		return self.getEntity(entityType, select, where, entityName)

	def getEntity(self, entityType, select, where, whereValue):
		results = self.getEntities(entityType, select, where,
				(whereValue,))

		return self.getFirstResult(results)

	def getEntities(self, entityType, select, where, values):
		replacements = ', '.join(['?'] * len(values))
		query = ('SELECT ' + select + ' FROM ' + entityType + 's '
				'WHERE ' + where + ' IN (' + replacements + ')')
		return self.execute(query, values).fetchall()

	def getFirstResult(self, results):
		return results[0] if (len(results) > 0) else None

	def getActorIdByName(self, actorName):
		return self.getEntityIdByName('Actor', actorName)

	def getActorsByName(self, actorNames):
		return self.getEntitiesByName('Actor', actorNames)

	def getEntitiesByName(self, entityType, entityNames):
		entityName = entityType + 'Name'
		selects = '*'
		where = entityName

		return self.getEntities(entityType, selects, where,
				entityNames)

	def getActorByName(self, actorName):
		results = self.getActorsByName((actorName,))
		result = self.getFirstResult(results)

		if not result:
			return result

		return {
			'ActorId': result['ActorId'],
			'ActorName': result['ActorName'],
			'Path': self.loadPickle(result['Path']),
			}

	def loadPickle(self, pickles):
		if pickles:
			try:
				return pickle.loads(pickles)

			except error:
				return pickles

		return pickles

	def getFilmsByName(self, filmNames):
		return self.getEntitiesByName('Film', filmNames)

	def getFilmByName(self, filmName):
		results = self.getFilmsByName((filmName,))

		return self.getFirstResult(results)

	def getFilmsById(self, filmIds):
		return self.getEntitiesById('Film', filmIds)

	def getEntitiesById(self, entityType, entityIds):
		entityName = entityType + 'Id'
		selects = '*'
		where = entityName

		return self.getEntities(entityType, selects, where,
				entityIds)

	def getActorsById(self, actorIds):
		return self.getEntitiesById('Actor', actorIds)

	def getFilmsByActorId(self, actorId):
		return self.getCastEntityByCounterId('Film', 'Actor', actorId)

	def getCastEntityByCounterId(self, entityColumn, counterColumn, id):
		return self.getEntities('Cast', entityColumn + 'Id',
				counterColumn + 'Id', (id, '',))

	def getActorsByFilmId(self, filmId):
		return self.getCastEntityByCounterId('Actor', 'Film', filmId)

	def addFilm(self, filmName):
		return self.addEntity('Film', filmName)

	def addEntity(self, entityType, entityNameValue):
		insert = ('INSERT INTO ' + entityType + 's (' + entityType + 'Name) '
				'VALUES (?)')
		self.execute(insert, (entityNameValue,))
		self.commit()

		return self.getCursor().lastrowid

	def addActor(self, actorName):
		return self.addEntity('Actor', actorName)

	def addCast(self, castMembers):
		insert = 'INSERT INTO Casts (FilmId, ActorId) VALUES (?, ?)'
		self.executemany(insert, castMembers)
		self.commit()

	def executemany(self, *args):
		return self.getCursor().executemany(*args)

	def revert(self):
		self.getConnection().rollback()
		self.end()

	def getConnection(self):
		if not self.connection:
			self.start()

		return self.connection

	def updateActorPaths(self, paths):
		update = 'UPDATE Actors SET Path = ? WHERE ActorId = ?'
		self.executemany(update, self.getUpdateForActorPaths(paths))
		self.commit()

	def getUpdateForActorPaths(self, paths):
		updateForActorPaths = ()

		for path in paths:
			updateForActorPaths += ((pickle.dumps(path[0]), str(path[1]),),)

		return updateForActorPaths

	def updateFilmsInPyramid(self, filmIds):
		update = 'UPDATE Films SET InPyramid = 1 WHERE FilmId = ?'
		self.executemany(update, self.getUpdateForFilmsInPyramid(filmIds))
		self.commit()

	def getUpdateForFilmsInPyramid(self, filmIds):
		updateForFilmsInPyramid = ()

		for filmId in filmIds:
			updateForFilmsInPyramid += (str(filmId),)

		return updateForFilmsInPyramid

	def updateBaconActorId(self, baconActorId):
		self.updateBaconValue('ActorId', baconActorId)

	def updateBaconValue(self, set, value):
		update = 'UPDATE Bacon SET ' + set + ' = (?) WHERE ROWID IN (?)'
		self.execute(update, (value, self.baconRowId,))
		self.commit()

	def updateBaconPyramid(self, pyramid):
		self.updateBaconValue('Pyramid', pickle.dumps(pyramid))

	def getBaconActorId(self):
		return self.getBaconValue('ActorId')

	def getBaconValue(self, value):
		query = 'SELECT ' + value +' FROM Bacon WHERE ROWID IN (?)'
		result = self.execute(query, (self.baconRowId,)).fetchone()

		return result[value]

	def getBaconPyramid(self):
		return self.loadPickle(self.getBaconValue('Pyramid'))

	def dropAll(self):
		if self.isSetup():
			os.remove(self.databasePath)

		return self