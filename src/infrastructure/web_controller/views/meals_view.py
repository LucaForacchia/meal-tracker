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

        self.meal_list = api.model("meal_list",
        {
            "week_number": fields.Integer(required = True),
            "total": fields.Integer(required = True),
            "meals": fields.List(fields.Nested(self.meal_model), required = True)
        })
        
        self.meal_form = api.model("meal_form", {
            "date": fields.String(required = True),
            "start_week": fields.Boolean(required = True),
            "meal_type": fields.String(required = True),
            "participants": fields.String(required = True),
            "meal": fields.String(required = True),
            "notes": fields.String(required = True)
        })


    def represent_meal(self, meal):
        return {
        "date": meal.date.isoformat(),
        "meal_type": meal.meal_type,
        "participants": meal.participants,
        "meal": meal.meal,
        "notes": meal.notes
        }
    
    def represent_meal_list(self, week_number, meal_list):
        return {
            "week_number": week_number,
            "total": len(meal_list),
            "meals": [self.represent_meal(meal) for meal in meal_list]
        }