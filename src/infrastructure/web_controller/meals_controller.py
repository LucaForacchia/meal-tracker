import logging
from flask import request
from flask_restx import Namespace, Resource, fields
from datetime import datetime, timezone

from .configuration import get_meal_repository
from .views.error_view import ErrorModel
from .views.meals_view import MealModel

api = Namespace("insertion",
                description="data reception service")

error_model = ErrorModel(api)
meal_model = MealModel(api)

def validate_input_datetime(arg_name, req_args, default = None):
    if arg_name in req_args:
        try:
            logging.info("Input parameter %s: %s" % (arg_name, req_args[arg_name]))
            timestamp_start = int(datetime.timestamp(datetime.fromisoformat(req_args[arg_name])))
        except ValueError as err:
            raise ValueError("Error in parameter %s: %s" % (arg_name, str(err)))
    else:
        if default is None:
            raise ValueError("Missing required parameter: " + arg_name)
        else:
            timestamp_start = default
    
    return timestamp_start

# This should become a constructor for the meal obkect (see tags in data-collector)
def validate_meal_form(form):
    # Check the meal form is well-formed, all fields are legal
    if form is None:
        raise InvalidFormError("request sent without meal_form")

    try:
        # Meal should become a domain object
        meal = {
            "date": datetime.fromisoformat(form["date"]),
            "start_week": bool(form["start_week"]),
            "meal_type": form["meal_type"],
            "participants": form["participants"],
            "meal": form["meal"],
            "notes": form["notes"]
        }
    except ValueError as err:
        raise InvalidFormError("Invalid value in input form, %s" % str(err))
    
    return meal

@api.route('/')
class SingleMeal(Resource):
    @api.doc('receive a session notification, compute chunks and store them into table')
    @api.response(201, 'Meal inserted')
    @api.response(400, 'Bad Request', model=error_model.error_view)
    @api.expect(meal_model.meal_form)
    def post(self):
        logging.info("meal received")        
        form = request.get_json()

        try:
            meal = validate_meal_form(form)
        except (KeyError, InvalidFormError) as err:
            return (error_model.represent_error(str(err)), 400)

        logging.info("Meal received, store")
        
        offset = 12*60*60 if meal["meal_type"] == "Pranzo" else 20*60*60
        meal["timestamp"] = meal["date"].timestamp() + offset
        
        # THIS SHOULD BE RETRIEVED IN COMPLEX WAYS FROM DB
        meal["meal_id"] = meal["meal"]

        meal["date"] = meal["date"].date().isoformat()
        repository = get_meal_repository()

        repository.insert_meal(meal)

        return ("Meal stored", 201)

    @api.doc('return last meal inserted')
    @api.response(200, 'Meal', model=meal_model.meal_model)
    @api.response(400, 'Bad Request', model=error_model.error_view)
    @api.response(404, 'Not Found', model=error_model.error_view)
    def get(self):
        logging.info("Requested last meal")
        try:
            return(meal_model.represent_meal(get_meal_repository().get_last_meal()), 200)
        except KeyError as err:
            return(error_model.represent_error(str(err)), 404)

@api.route('/week')
class WeeklyMealList(Resource):
    @api.doc('return weekly meal list')
    @api.response(200, 'Meal', model=meal_model.meal_list)
    @api.response(400, 'Bad Request', model=error_model.error_view)
    @api.response(404, 'Not Found', model=error_model.error_view)
    def get(self):
        logging.info("Requested week meals")
        week_number = int(request.args["week-number"]) if "week-number" in request.args else None

        week_number, meals_list = get_meal_repository().get_weekly_meals(week_number)
        return meal_model.represent_meal_list(week_number, meals_list)

class InvalidFormError(Exception):
    pass