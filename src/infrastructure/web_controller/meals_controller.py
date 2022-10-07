import logging
from flask import request
from flask_restx import Namespace, Resource, fields
from datetime import datetime, timezone

from domain.meal import Meal

from .configuration import get_meal_service
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
        form["date"] = datetime.fromisoformat(form["date"])
        form["start_week"] = bool(form["start_week"])
    except ValueError as err:
        raise InvalidFormError("Invalid value in input form, %s" % str(err))
    
    return Meal(**form)

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
        
        get_meal_service().store_meal(meal)

        return ("Meal stored", 201)

    @api.doc('return last meal inserted')
    @api.response(200, 'Meal', model=meal_model.meal_model)
    @api.response(400, 'Bad Request', model=error_model.error_view)
    @api.response(404, 'Not Found', model=error_model.error_view)
    def get(self):
        logging.info("Requested last meal")
        try:
            return(meal_model.represent_meal(get_meal_service().get_last_meal()), 200)
        except KeyError as err:
            return(error_model.represent_error(str(err)), 404)

# @api.route('/single/<meal-id>')
# class SingleMeal(Resource):
#     @api.doc('delete a meal')
#     @api.response(204, 'Meal Deleted')
#     @api.response(400, 'Bad Request', model=error_model.error_view)
#     @api.response(404, 'Not Found', model=error_model.error_view)
#     def delete(self):
#         logging.info("Request to delete a meal")
#         ## TO BE IMPLEMENTED
#         return 204

@api.route('/week')
class WeeklyMealList(Resource):
    @api.doc('return weekly meal list')
    @api.response(200, 'Meal', model=meal_model.meal_list)
    @api.response(400, 'Bad Request', model=error_model.error_view)
    @api.response(404, 'Not Found', model=error_model.error_view)
    def get(self):
        logging.info("Requested week meals")
        week_number = int(request.args["week-number"]) if "week-number" in request.args else None

        week_number, meals_list = get_meal_service().get_weekly_meals(week_number)
        return meal_model.represent_meal_list(week_number, meals_list)

@api.route('/counts')
class MealsCount(Resource):
    @api.doc('return count of meals')
    @api.response(200, 'Meal', model=meal_model.meal_counts)
    @api.response(400, 'Bad Request', model=error_model.error_view)
    def get(self):
        logging.info("returning meals count")
        meal_counts = get_meal_service().get_meals_count()
        return meal_model.represent_meal_count(meal_counts)

class InvalidFormError(Exception):
    pass