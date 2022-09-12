from json import loads
import logging

class MealService():
    def __init__(self, db, config):
        self.db = db
        self.config = config

    def build_meal_id(self, meal):
        return str(meal).upper().replace(" E ", "").replace(",", "").replace(" ","")

    def store_meal(self, meal):
        offset = 12*60*60 if meal["meal_type"] == "Pranzo" else 20*60*60
        meal["timestamp"] = meal["date"].timestamp() + offset
        
        # THIS SHOULD BE RETRIEVED IN COMPLEX WAYS FROM DB
        meal["meal_id"] = self.build_meal_id(meal["meal"])

        meal["date"] = meal["date"].date().isoformat()
        
        if meal["start_week"]:
            week_number, _ = self.repository.get_last_week_timestamp()
            meal["start_week"] = week_number + 1

        return meal

