from datetime import date, datetime

class Meal:
    def __init__(self, meal_date, meal_type, participants, meal, notes):
        self.date = date.fromisoformat(meal_date)
        self.meal_type = meal_type
        self.participants = participants
        self.meal = meal
        self.notes = notes