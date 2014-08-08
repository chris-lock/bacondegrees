#!/usr/bin/env python

import os
import sqlite3
from baconhelpers import printAndExit
import pickle

## A seach object abstarted so it can be swapped out. Currently uses SQLite.
#
#  @author Chris Lock
class BaconSearch():
	# @constant The row to add Kevin at in the Bacon table
	BACON_ROW_ID = 1

	# @type {string} The absolute path to the directory that this file lives in
	directory = os.path.dirname(os.path.realpath(__file__))
	# @type {object} The connection object
	connection = None
	# @type {string} The path to the database
	databasePath = directory + '/baconsearch.db'
	# @type {dictionary} The tables for the database
	databaseTables = {
		'Bacon': 'ActorId INT, Pyramid TEXT',
		'Actors': 'ActorId INTEGER PRIMARY KEY, '
				'ActorName VARCHAR COLLATE NOCASE, Result TEXT, '
				'BaconDegrees Int',
		'Films': 'FilmId INTEGER PRIMARY KEY, FilmName VARCHAR',
		'Casts': 'FilmId INT, ActorId INT',
		}
	# @type {object} The cursor object
	cursor = None

	## An empty constructor.
	#
	#  @param {object} self The object
	#  @return void
	def __init__(self):
		pass

	## Creates the database tables if they don't exist.
	#
	#  @param {object} self The object
	#  @return {object} The object for chaining
	def setup(self):
		if not self.__isSetup():
			self.start().__createDatabaseTables().end()

		return self

	## Checks if the databse is set up.
	#
	#  @param {object} self The object
	#  @return {bool} The database exists
	def __isSetup(self):
		return os.path.isfile(self.databasePath)

	## Starts the database connection. Adds the row factory to return 
	#  dictionaries. Sets the cursor object.
	#
	#  @param {object} self The object
	#  @return {object} The object for chaining
	def start(self):
		if self.connection:
			return self

		try:
			self.connection = sqlite3.connect(self.databasePath)
			self.connection.row_factory = sqlite3.Row
			self.cursor = self.connection.cursor()

			return self

		except sqlite3.Error, error:
			printAndExit('Error %s:' % error.args[0])

	## Creates the database tables and adds the BBacon row to the Bacon table
	#  for Kevin's stuff.
	#
	#  @param {object} self The object
	#  @return {object} The object for chaining
	def __createDatabaseTables(self):
		for (tableName, columns) in self.databaseTables.items():
			create = ('CREATE TABLE IF NOT EXISTS ' + tableName +
					'(' + columns + ')')
			self.__execute(create)

		insert = (''
				'INSERT OR REPLACE INTO Bacon '
				'(ROWID, ActorId) '
				'VALUES (?, ?)')
		self.__execute(insert, (self.BACON_ROW_ID, 0,))

		return self

	## A wrapper for execute to dry code out.
	#
	#  @param {object} self The object
	#  @param {args} *args the arguments for execute
	#  @return {object} The cursor object or results
	def __execute(self, *args):
		return self.__getCursor().execute(*args)

	## Gets the cursor object. If there's non, we probably don't have a 
	#  connection so we should start one.
	#
	#  @param {object} self The object
	#  @return {object} The cursor object
	def __getCursor(self):
		if not self.cursor:
			self.start()

		return self.cursor

	## Clears all cached data columns.
	#
	#  @param {object} self The object
	#  @return void
	def clearCache(self):
		self.__execute(''
				'UPDATE Bacon '
				'SET Pyramid = NULL')
		self.__execute(''
				'UPDATE Actors '
				'SET Result = NULL, BaconDegrees = NULL')
		self.__commit()

	## Commits any changes and closes the connection if we had one.
	#
	#  @param {object} self The object
	#  @return void
	def end(self):
		self.__commit()

		if self.connection:
			self.connection.close()
			self.connection = None
			self.cursor = None

	## Commits any changes. If we don't have a connection we'll need one, but
	#  this scenario is super unlikely. Just being safe.
	#
	#  @param {object} self The object
	#  @return {object} The object for chaining
	def __commit(self):
		if self.connection:
			self.connection.commit()

		return self

	## Gets a film id by a film name.
	#
	#  @param {object} self The object
	#  @param {string} filmName The film name
	#  @return {mixed} None or a dictionary
	def getFilmIdByName(self, filmName):
		return self.__getEntityIdByName('Film', filmName)

	## Gets a film or actor id by a it's name.
	#
	#  @param {object} self The object
	#  @param {string} entityType A film or actor
	#  @param {string} entityName The entity name
	#  @return {mixed} None or a dictionary
	def __getEntityIdByName(self, entityType, entityName):
		select = entityType + 'Id'
		where = entityType + 'Name'

		return self.__getEntity(entityType, select, where, entityName)

	## Gets a film or actor value by a where value.
	#
	#  @param {object} self The object
	#  @param {string} entityType A film or actor
	#  @param {string} select What to select
	#  @param {string} where The were column or columns
	#  @param {string} value The values for the where to match
	#  @return {mixed} None or a dictionary
	def __getEntity(self, entityType, select, where, value):
		results = self.__getEntities(entityType, select, where, (value,))

		return self.__getFirstResult(results)

	## Gets films or actors value by a where value.
	#
	#  @param {object} self The object
	#  @param {string} entityType A film or actor
	#  @param {string} select What to select
	#  @param {string} where The were column or columns
	#  @param {string} values The values for the where to match
	#  @return {list} A list of results
	def __getEntities(self, entityType, select, where, values):
		valuesString = ', '.join(['?'] * len(values))
		query = ('SELECT ' + select + ' '
				'FROM ' + entityType + 's '
				'WHERE ' + where + ' IN (' + valuesString + ') ')

		return self.__execute(query, values).fetchall()

	## Gets the first results from a list of results or returns None if there
	#  are none.
	#
	#  @param {object} self The object
	#  @param {list} results A film or actor
	#  @return {mixed} None or a dictionary
	def __getFirstResult(self, results):
		return results[0] if (len(results) > 0) else None

	## Gets an actor id by an actor name.
	#
	#  @param {object} self The object
	#  @param {string} actorName The actor name
	#  @return {mixed} None or a dictionary
	def getActorIdByName(self, actorName):
		return self.__getEntityIdByName('Actor', actorName)

	## Gets a set of actors info from their names.
	#
	#  @param {object} self The object
	#  @param {tuple} actorNames Actor names
	#  @return {mixed} None or a dictionary
	def getActorsByName(self, actorNames):
		return self.__getEntitiesByName('Actor', actorNames)


	## Gets a set of actors or films info by their names.
	#
	#  @param {object} self The object
	#  @param {string} entityType A film or actor
	#  @param {tuple} entityNames The entity names
	#  @return {mixed} None or a dictionary
	def __getEntitiesByName(self, entityType, entityNames):
		entityName = entityType + 'Name'
		selects = '*'
		where = entityName

		return self.__getEntities(entityType, selects, where, entityNames)

	## Gets an actor's info by a name.
	#
	#  @param {object} self The object
	#  @param {string} actorName The actor name
	#  @return {mixed} None or a dictionary
	def getActorByName(self, actorName):
		results = self.getActorsByName((actorName,))
		result = self.__getFirstResult(results)

		if not result:
			return result

		return {
			'ActorId': result['ActorId'],
			'ActorName': result['ActorName'],
			'Result': self.__loadPickle(result['Result']),
			}

	## A wrapper for loading a pickle.
	#
	#  @param {object} self The object
	#  @param {string} pickles The result of the previosu pickling
	#  @return {object} The pickled object
	def __loadPickle(self, pickles):
		if pickles:
			try:
				return pickle.loads(pickles)

			except error:
				return pickles

		return pickles

	## Gets a set of films info by their names.
	#
	#  @param {object} self The object
	#  @param {tuple} filmNames Film names
	#  @return {mixed} None or a dictionary
	def getFilmsByName(self, filmNames):
		return self.__getEntitiesByName('Film', filmNames)

	## Gets an film's info by a name.
	#
	#  @param {object} self The object
	#  @param {string} filmName The film name
	#  @return {mixed} None or a dictionary
	def getFilmByName(self, filmName):
		results = self.getFilmsByName((filmName,))

		return self.__getFirstResult(results)

	## Gets a set of films' info by their ids.
	#
	#  @param {object} self The object
	#  @param {tuple} filmIds The film ids
	#  @return {mixed} None or a dictionary
	def getFilmsById(self, filmIds):
		return self.__getEntitiesById('Film', filmIds)

	## Gets a set of films' or actors' info by their ids.
	#
	#  @param {object} self The object
	#  @param {string} entityIds The film ids
	#  @return {mixed} None or a dictionary
	def __getEntitiesById(self, entityType, entityIds):
		entityName = entityType + 'Id'
		selects = '*'
		where = entityName

		return self.__getEntities(entityType, selects, where, entityIds)

	## Gets a set of films' or actors' info by their ids.
	#
	#  @param {object} self The object
	#  @param {tuple} entityIds The film ids
	#  @return {mixed} None or a dictionary
	def getActorsById(self, actorIds):
		return self.__getEntitiesById('Actor', actorIds)

	## Gets a set of film ids for a given actor id from the Casts table
	#
	#  @param {object} self The object
	#  @param {string} actorId The actor id
	#  @return {mixed} None or a dictionary
	def getFilmsByActorId(self, actorId):
		return self.__getCastEntityByCounterId('Film', 'Actor', actorId)

	## Gets either a set of film ids from an actor id or vice versa.
	#
	#  @param {object} self The object
	#  @param {string} entityColumn The entity to get
	#  @param {string} counterColumn It's counter in the table
	#  @param {string} id The counter's id
	#  @return {mixed} None or a dictionary
	def __getCastEntityByCounterId(self, entityColumn, counterColumn, id):
		return self.__getEntities('Cast', entityColumn + 'Id',
				counterColumn + 'Id', (id, '',))

	## Gets a set of actor ids for a given film id from the Casts table
	#
	#  @param {object} self The object
	#  @param {string} filmId The film id
	#  @return {mixed} None or a dictionary
	def getActorsByFilmId(self, filmId):
		return self.__getCastEntityByCounterId('Actor', 'Film', filmId)

	## Adds a film to the table.
	#
	#  @param {object} self The object
	#  @param {string} filmName The film name
	#  @return {string} The id of the added film
	def addFilm(self, filmName):
		return self.__addEntity('Film', filmName)

	## Adds a film or actor to the table.
	#
	#  @param {object} self The object
	#  @param {string} entityType A film or actor
	#  @param {string} entityNameValue The film or actor name
	#  @return {string} The id of the added entity
	def __addEntity(self, entityType, entityNameValue):
		insert = ('INSERT INTO ' + entityType + 's '
				'(' + entityType + 'Name) '
				'VALUES (?)')
		self.__execute(insert, (entityNameValue,))
		self.__commit()

		return self.__getCursor().lastrowid

	## Adds a actor to the table.
	#
	#  @param {object} self The object
	#  @param {string} actorName The actor name
	#  @return {string} The id of the added actor
	def addActor(self, actorName):
		return self.__addEntity('Actor', actorName)

	## Adds a cast being a set of corresponding film ids with actors ids.
	#
	#  @param {object} self The object
	#  @param {tuple} castMembers The film id then actor id
	#  @return void
	def addCast(self, castMembers):
		insert = ('INSERT INTO Casts '
				'(FilmId, ActorId) '
				'VALUES (?, ?)')
		self.__executemany(insert, castMembers)
		self.__commit()

	## A wrapper for execute many.
	#
	#  @param {object} self The object
	#  @param {args} *args The arguments for execute many
	#  @return {object} The cursor object
	def __executemany(self, *args):
		return self.__getCursor().executemany(*args)

	## Reverts any pending changes to the database.
	#
	#  @param {object} self The object
	#  @return void
	def revert(self):
		self.__getConnection().rollback()
		self.end()

	## Gets the connection. If none, starts one.
	#
	#  @param {object} self The object
	#  @return {object} The connection object
	def __getConnection(self):
		if not self.connection:
			self.start()

		return self.connection

	## Updates actor results in sets of 100 to be safe.
	#
	#  @param {object} self The object
	#  @param {tuple} results A tuple of tuples (result, bacon degrees, id)
	#  @return void
	def updateActorResults(self, results):
		update = ('UPDATE Actors '
				'SET Result = ?, BaconDegrees = ? '
				'WHERE ActorId = ?')

		for actorResultsUpdateSet in self.__getActorResultsUpdateSets(results):
			self.__executemany(update, actorResultsUpdateSet)

		self.__commit()

	## Builds sets of 100 tuples for updates.
	#
	#  @param {object} self The object
	#  @param {tuple} results A tuple of tuples (result, bacon degrees, id)
	#  @return {list} Sets of 100 actor updates
	def __getActorResultsUpdateSets(self, results):
		index = 0
		actorResultsUpdateSets = []
		actorResultsUpdateSet = ()

		for path in results:
			if index and index % 100 == 0:
				actorResultsUpdateSets.append(actorResultsUpdateSet)
				actorResultsUpdateSet = ()

			actorResultsUpdateSet += ((pickle.dumps(path[0]), str(path[1]),
					str(path[2]),),)

			index += 1

		actorResultsUpdateSets.append(actorResultsUpdateSet)

		return actorResultsUpdateSets

	## Updates Kevo's actor id and sets his path and degrees in the actor table.
	#
	#  @param {object} self The object
	#  @param {string} baconActorId Kevin Bacon's actor id
	#  @return {void}
	def updateBaconActorId(self, baconActorId):
		self.__updateBaconValue('ActorId', baconActorId)
		self.updateActorResults((('', '0', baconActorId,),))

	## Updates a given value in the Bacon table.
	#
	#  @param {object} self The object
	#  @param {string} set The value to set
	#  @param {string} value The value to set it to
	#  @return {void}
	def __updateBaconValue(self, set, value):
		update = ('UPDATE Bacon '
				'SET ' + set + ' = (?) '
				'WHERE ROWID IN (?)')
		self.__execute(update, (value, self.BACON_ROW_ID,))
		self.__commit()

	## Saves the state of the bacon pyramid in a pickle in the table.
	#
	#  @param {object} self The object
	#  @param {dictionary} pyramid The pyramid
	#  @return {void}
	def updateBaconPyramid(self, pyramid):
		self.__updateBaconValue('Pyramid', pickle.dumps(pyramid))

	## Gets Kevin Bacon's actor id from the Bacon table so the look up is 
	#  quicker.
	#
	#  @param {object} self The object
	#  @return {string} Kevo's actor id
	def getBaconActorId(self):
		return self.__getBaconValue('ActorId')

	## Gets a value from a column in the Bacon table.
	#
	#  @param {object} self The object
	#  @return {string} column The value column
	#  @return {string} The value
	def __getBaconValue(self, column):
		query = ('SELECT ' + column +' '
				'FROM Bacon '
				'WHERE ROWID IN (?)')
		result = self.__execute(query, (self.BACON_ROW_ID,)).fetchone()

		return result[value]

	## Gets the pyramid object from the database
	#
	#  @param {object} self The object
	#  @return {dictionary} The pyramid
	def getBaconPyramid(self):
		return self.__loadPickle(self.__getBaconValue('Pyramid'))

	## Films are islands not actors so we get all the films with actor's who
	#  have no bacon degrees. We assume the pyrmiad has been solved or this
	#  will be inaccurate.
	#
	#  @param {object} self The object
	#  @return {dictionary} The films and their actors
	def getUnsolved(self):
		unsolvedFilms = {}

		query = ('SELECT  Films.FilmName, Actors.ActorName '
				'FROM Actors '
				'NATURAL JOIN Casts '
				'NATURAL JOIN Films '
				'WHERE Actors.BaconDegrees IS NULL ')

		for result in self.__execute(query).fetchall():
			if result['FilmName'] not in unsolvedFilms:
				unsolvedFilms[result['FilmName']] = []

			unsolvedFilms[result['FilmName']].append(result['ActorName'])

		return unsolvedFilms

	## Deletes the entire database.
	#
	#  @param {object} self The object
	#  @return void
	def clearAll(self):
		if self.__isSetup():
			os.remove(self.databasePath)

		return self