from json import loads, dumps
import sqlite3
from mysql.connector.errors import IntegrityError as MySqlIntegrityError
import logging
from uuid import uuid4
from datetime import datetime
from collections import Counter

from domain.meal import Meal
from domain.meal_occurrences import MealOccurrences

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

        c.execute(self.__mysql_query_adapter__('''
            CREATE TABLE IF NOT EXISTS meal_counter (
                meal_id VARCHAR(50) NOT NULL,
                meal TEXT NOT NULL,
                count_total INT NOT NULL DEFAULT 0,
                both INT NOT NULL DEFAULT 0,
                L INT NOT NULL DEFAULT 0,
                G INT NOT NULL DEFAULT 0,
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

    def __serialize_row__(self, row):
        return Meal(datetime.fromisoformat(row[0]), row[1], row[2], row[3], row[4], start_week = bool(row[5]))

    ''' These 2 method needs to be unified to v2'''
    def update_meal_counter_v2(self, meal_occurrences, replaced = None):
        c = self.db.cursor()

        c.execute(self.__mysql_query_adapter__('''
            SELECT 
                count_total,
                both,
                L,
                G
            FROM meal_counter where meal_id = ?
            LIMIT 1
        '''), [meal_occurrences.meal_id])

        meal_selected = c.fetchone()

        if meal_selected is None:
            if meal_occurrences.name is None:
                raise Exception("Name not specified! Unable to insert into meal counter table")
            c.execute(self.__mysql_query_adapter__('''
                INSERT INTO meal_counter (
                    meal_id,
                    meal,
                    count_total,
                    both,
                    L,
                    G
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    '''), (meal_occurrences.meal_id, meal_occurrences.name, meal_occurrences.total, 
                    meal_occurrences.both, meal_occurrences.l, meal_occurrences.g))
        else:
            c.execute(self.__mysql_query_adapter__('''
                UPDATE meal_counter
                SET
                    count_total = ?,
                    both = ?,
                    L = ?,
                    G = ?
                WHERE meal_id = ?
            '''), (meal_selected[0] + meal_occurrences.total, meal_selected[1] + meal_occurrences.both, 
            meal_selected[2] + meal_occurrences.l, meal_selected[3] + meal_occurrences.g, meal_occurrences.meal_id))

        if replaced is not None:
            c.execute(self.__mysql_query_adapter__('''
                DELETE FROM meal_counter WHERE meal_id = ?
            '''), [replaced])
            
        self.db.commit()

    def update_meal_counter(self, meal):
        c = self.db.cursor()

        plus_both = 1 if meal.participants == "Entrambi" else 0 
        plus_l = 1 if meal.participants == "Luca" else 0
        plus_g = 1 if meal.participants == "Gioi" else 0

        c.execute(self.__mysql_query_adapter__('''
            SELECT 
                count_total,
                both,
                L,
                G
            FROM meal_counter where meal_id = ?
            LIMIT 1
        '''), [meal.meal_id])

        meal_selected = c.fetchone()

        if meal_selected is None:
            c.execute(self.__mysql_query_adapter__('''
                INSERT INTO meal_counter (
                    meal_id,
                    meal,
                    count_total,
                    both,
                    L,
                    G
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    '''), (meal.meal_id, meal.meal, 1, plus_both, plus_l, plus_g))
        else:
            c.execute(self.__mysql_query_adapter__('''
                UPDATE meal_counter
                SET
                    count_total = ?,
                    both = ?,
                    L = ?,
                    G = ?
                WHERE meal_id = ?
            '''), (meal_selected[0] + 1, meal_selected[1] + plus_both, meal_selected[2] + plus_l, meal_selected[3] + plus_g, meal.meal_id))

        self.db.commit()

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

        logging.debug("Inserting meal %s" % (meal.__dict__))
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
                    '''), (meal.date, meal.timestamp, meal.week_number if meal.start_week else 0, meal.meal_type, 
                        meal.participants, meal.meal, meal.meal_id, meal.notes))

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
                notes,
                start_week
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
                notes,
                start_week
            FROM meals
            WHERE timestamp >= ? AND timestamp < ?
            ORDER BY timestamp ASC
        '''), (timestamps[0], timestamps[1]))

        return week_number, [self.__serialize_row__(row) for row in c.fetchall()]                

    def get_meals_count(self, filter = None):
        c = self.db.cursor()

        c.execute(self.__mysql_query_adapter__('''
            SELECT meal_id, meal, count_total 
            FROM meal_counter
        '''))

        return {row[0]: {"name": row[1], "count": row[2]} for row in c.fetchall() if row[1] != ""}

    def get_meal_occurrences(self, meal_id):
        c = self.db.cursor()

        c.execute(self.__mysql_query_adapter__('''
            SELECT 
            participants 
            FROM MEALS WHERE meal_id = ?
        '''), [meal_id])

        participants_list = [x[0] for x in c.fetchall()]

        counts = Counter(participants_list)
        
        return MealOccurrences(meal_id=meal_id, total = len(participants_list), both = counts["Entrambi"],
            l = counts["Luca"], g = counts["Gioi"])
    
    def get_meals_names(self, filter = None):
        c = self.db.cursor()

        c.execute(self.__mysql_query_adapter__('''
            SELECT meal 
            FROM meal_counter
        '''))

        return [x[0] for x in c.fetchall()]

class DuplicateMeal(Exception):
    pass

class MealNotFound(KeyError):
    pass
