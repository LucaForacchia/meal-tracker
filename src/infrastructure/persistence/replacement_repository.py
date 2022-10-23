from json import loads, dumps
import sqlite3
from mysql.connector.errors import IntegrityError as MySqlIntegrityError
import logging
from uuid import uuid4
from datetime import datetime

from domain.meal import Meal

class ReplacementRepository:
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
            CREATE TABLE IF NOT EXISTS aka (
                meal_id VARCHAR(255) NOT NULL,
                replacement VARCHAR(255) NOT NULL,
                PRIMARY KEY(meal_id)
            )
        '''))

        self.db.commit()

    def __del__ (self):
        try:
            self.db.close()
        except Exception as err:
            print("error while closing the connection:", err)
            pass

    def get_akas_dict(self):
        c = self.db.cursor()

        c.execute('''
            SELECT
                meal_id,
                replacement
            FROM aka
            ''')

        return {x[0]: x[1] for x in c.fetchall()}

    def insert_aka(self, meal_id, aka):
        c = self.db.cursor()

        c.execute(self.__mysql_query_adapter__('''
            INSERT INTO aka (
                meal_id,
                replacement
            ) VALUES (?,?)
            '''), (meal_id, aka)) 

        self.db.commit()