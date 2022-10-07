from json import loads
import logging

from infrastructure.persistence.meal_repository import MealRepository

class MealService():
    def __init__(self, db, config):
        self.db = db
        self.config = config
        self.repository = MealRepository(db, config["db_type"])

    def store_meal(self, meal):
        if meal.start_week:
            logging.debug("New week, retrieving week number")
            week_number, _ = self.repository.get_last_week_timestamp()
            logging.debug("Starting week number %d" % (week_number + 1))
            meal.week_number = week_number + 1
        self.repository.insert_meal(meal)

    def get_last_meal(self):
        return self.repository.get_last_meal()

    def get_weekly_meals(self, week_number):
        return self.repository.get_weekly_meals(week_number)

    def get_meals_count(self):
        meals_count = self.repository.get_meals_count()

        return self.group_id(meals_count)



    def group_id(self, meals_count):
        # HERE I SHOULD INSERT LOGIC TO GROUP MEAL COUNT

        # SUPPOSE I'VE A MAGIC TABLE WITH ALL THE MEAL_ID TO BE REPLACED

        magic_table = {
            "NORMADISPADA": "NORMADIPESCESPADA",
            "CROSTINISTRACCHINOSALSICCIA": "CROSTINISALSICCIASTRACCHINO",
            "CROSTINIDISALSICCIASTRACCHINO": "CROSTINISALSICCIASTRACCHINO"
        }

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
                