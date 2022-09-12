from json import loads, dumps
import sqlite3
from mysql.connector.errors import IntegrityError as MySqlIntegrityError
import logging
from uuid import uuid4
from datetime import datetime

from domain.meal import Meal

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
                timestamp INT NOT NULL,
                start_week INT NOT NULL,
                type VARCHAR(50) NOT NULL,
                participants VARCHAR(50) NOT NULL,
                meal TEXT,
                meal_id TEXT NOT NULL,
                notes TEXT,
                PRIMARY KEY(timestamp, participants)
            )
        '''))

        self.db.commit()

    def __del__ (self):
        try:
            self.db.close()
        except Exception as err:
            print("error while closing the connection:", err)
            pass

    def __serialize_row__(self, row):
        return Meal(row[0], row[1], row[2], row[3], row[4])

    def get_last_week_timestamp(self):
        c = self.db.cursor()

        c.execute('''
            SELECT
                timestamp, start_week
            FROM meals
            WHERE start_week > 1
            ORDER BY timestamp desc
            LIMIT 1
            ''')

        row = c.fetchone()
        return row[1], (row[0], row[0] + 1209600)

    def __get_week_timestamp__(self, week_number):
        c = self.db.cursor()

        c.execute(self.__mysql_query_adapter__('''
            SELECT
                timestamp
            FROM meals
            WHERE start_week < ? AND start_week >= ?
            ORDER BY timestamp desc
            '''), (week_number + 2, week_number))

        rows = c.fetchall()
        if len(rows) > 2:
            raise Exception("Too many rows selected!!!")
        
        return week_number, (rows[1][0], rows[0][0])

    def insert_meal(self, meal):
        c = self.db.cursor()

        logging.debug("Inserting meal %s" % (str(meal)))
        try:
            c.execute(self.__mysql_query_adapter__('''
                    INSERT INTO meals (
                        date,
                        timestamp,
                        start_week,
                        type,
                        participants,
                        meal,
                        meal_id,
                        notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    '''), (meal["date"], meal["timestamp"], int(meal["start_week"]), meal["meal_type"], 
                        meal["participants"], meal["meal"], meal["meal_id"], meal["notes"]))

            self.db.commit()

        except (sqlite3.IntegrityError, MySqlIntegrityError):
            raise DuplicateMeal("A meal with same date type and participants already exists")

    def get_last_meal(self):
        c = self.db.cursor()
        c.execute('''
            SELECT DISTINCT date FROM meals
        ''')

        dates = sorted([datetime.fromisoformat(row[0]) for row in c.fetchall()], reverse=True)
        if len(dates) < 1:
            raise MealNotFound("Db is empty!")

        date = dates[0].isoformat().split("T")[0]

        c.execute(self.__mysql_query_adapter__('''
            SELECT 
                date,
                type,
                participants,
                meal,
                notes 
            FROM meals
            WHERE date = ? LIMIT 1
        '''), [date])

        row = c.fetchone()

        return self.__serialize_row__(row)
    
    def get_weekly_meals(self, week_number = None):
        c = self.db.cursor()

        week_number, timestamps = self.get_last_week_timestamp() if week_number is None else self.__get_week_timestamp__(week_number)
        
        c.execute(self.__mysql_query_adapter__('''
            SELECT 
                date,
                type,
                participants,
                meal,
                notes 
            FROM meals
            WHERE timestamp >= ? AND timestamp < ?
            ORDER BY timestamp ASC
        '''), (timestamps[0], timestamps[1]))

        return week_number, [self.__serialize_row__(row) for row in c.fetchall()]                

    def get_meals_count(self, filter = None):
        c = self.db.cursor()

        c.execute(self.__mysql_query_adapter__('''
            SELECT meal, meal_id, count(meal_id) 
            FROM meals 
            GROUP by meal_id
        '''))

        return sorted([(row[0], row[2]) for row in c.fetchall()], key = lambda x: x[1], reverse = True)

class DuplicateMeal(Exception):
    pass

class MealNotFound(KeyError):
    pass
