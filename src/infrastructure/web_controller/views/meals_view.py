from flask_restx import fields

class MealModel:
    def __init__(self, api):
        self.meal_model = api.model("meal",
        {
        "date": fields.String(required = True, description = "meal date"),
        "meal_type": fields.String(required = True),
        "participants": fields.String(required = True),
        "meal": fields.String(required = False),
        "notes": fields.String(required = False)
        } )

    def represent_meal(self, meal):
        return {
        "date": meal.date.isoformat(),
        "meal_type": meal.meal_type,
        "participants": meal.participants,
        "meal": meal.meal,
        "notes": meal.notes
        }