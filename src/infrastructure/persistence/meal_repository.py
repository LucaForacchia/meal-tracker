from json import loads, dumps
import sqlite3
from mysql.connector.errors import IntegrityError as MySqlIntegrityError
import logging
from uuid import uuid4

class MealRepository:
    def __init__(self, db, db_type="sqlite"):
        self.db = db
        self.db_type = db_type

        self.__create_tables__()

    def __mysql_query_adapter__(self, query):
        if self.db_type=="mysql":
            return query.replace("?", "%s")
        return query

    def __create_tables__ (self):
        c = self.db.cursor()

        c.execute(self.__mysql_query_adapter__('''
            CREATE TABLE IF NOT EXISTS meals (
                date VARCHAR(255) NOT NULL,
                start_week INT NOT NULL,
                type VARCHAR(50) NOT NULL,
                participants VARCHAR(50) NOT NULL,
                meal TEXT,
                notes TEXT,
                PRIMARY KEY(date, type, participants)
            )
        '''))

        self.db.commit()

    def __del__ (self):
        try:
            self.db.close()
        except Exception as err:
            print("error while closing the connection:", err)
            pass

    def insert_meal(self, date, start_week, type, participants, meal, notes):
        c = self.db.cursor()

        try:
            c.execute(self.__mysql_query_adapter__('''
                    INSERT INTO meals (
                        date,
                        start_week,
                        type,
                        participants,
                        meal,
                        notes
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    '''), (date, int(start_week), type, participants, meal, notes))

            self.db.commit()

        except (sqlite3.IntegrityError, MySqlIntegrityError):
            raise DuplicateMeal("A meal with same date type and participants already exists")


class DuplicateMeal(Exception):
    pass
