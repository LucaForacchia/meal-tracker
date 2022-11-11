from json import loads
import logging

from infrastructure.persistence.meal_repository import MealRepository
from infrastructure.persistence.replacement_repository import ReplacementRepository

class MealService():
    def __init__(self, db, config):
        self.db = db
        self.config = config
        self.repository = MealRepository(db, config["db_type"])
        self.replacement_repository = ReplacementRepository(db, config["db_type"])

    def store_meal(self, meal):
        if meal.start_week:
            logging.debug("New week, retrieving week number")
            week_number, _ = self.repository.get_last_week_timestamp()
            logging.debug("Starting week number %d" % (week_number + 1))
            meal.week_number = week_number + 1

        self.repository.insert_meal(meal)

        if meal.meal_id != "":
            # CHECK IF MEAL_ID HAS TO BE REPLACED
            aka_dict = self.replacement_repository.get_akas_dict()
            if meal.meal_id in aka_dict:
                meal.meal_id = aka_dict[meal.meal_id]

            self.repository.update_meal_counter(meal)

    def get_last_meal(self):
        return self.repository.get_last_meal()

    def get_weekly_meals(self, week_number):
        return self.repository.get_weekly_meals(week_number)

    def get_meals_count(self):
        meals_count = self.repository.get_meals_count()

        return self.group_id(meals_count)

    def get_meal_list(self):
        return self.repository.get_meals_names()

    def insert_aka(self, meal_id, aka):
        # TRY CATCH, IF THE AKA ALREADY IN TABLE?
        self.replacement_repository.insert_aka(meal_id, aka)

        # COUNT OCCURRENCE OF REPLACED ID IN MEAL TABLE
        meal_occurrences = self.repository.get_meal_occurrences(meal_id)

        meal_occurrences.meal_id = aka

        self.repository.update_meal_counter_v2(meal_occurrences, replaced = meal_id)

    def get_replacements(self):
        return self.replacement_repository.get_replacements()

    ''' This should become useless'''
    def group_id(self, meals_count):
        # HERE I SHOULD INSERT LOGIC TO GROUP MEAL COUNT

        # SUPPOSE I'VE A MAGIC TABLE WITH ALL THE MEAL_ID TO BE REPLACED

        # magic_table = {
        #     "NORMADISPADA": "NORMADIPESCESPADA",
        #     "CROSTINISTRACCHINOSALSICCIA": "CROSTINISALSICCIASTRACCHINO",
        #     "CROSTINIDISALSICCIASTRACCHINO": "CROSTINISALSICCIASTRACCHINO"
        # }

        magic_table = self.replacement_repository.get_akas_dict()
        
        dict_ids = list(meals_count.keys())

        for key in dict_ids:
            if key in magic_table:
                new_id = magic_table[key]

                if new_id in meals_count:
                    meals_count[new_id]["count"] += meals_count[key]["count"]
                else:
                    meals_count[new_id] = {
                        "name": meals_count[key]["name"],
                        "count": meals_count[key]["count"]
                        }
                del meals_count[key]

        return meals_count
                