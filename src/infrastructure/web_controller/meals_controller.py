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

meal_form = api.model("meal_form", {
    "date": fields.String(required = True),
    "start_week": fields.Boolean(required = True),
    "meal_type": fields.String(required = True),
    "participants": fields.String(required = True),
    "meal": fields.String(required = True),
    "notes": fields.String(required = True)
})

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
            "date": datetime.fromisoformat(form["date"]).date(),
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
class StressList(Resource):
    @api.doc('receive a session notification, compute chunks and store them into table')
    @api.response(201, 'Meal inserted')
    @api.response(400, 'Bad Request', model=error_model.error_view)
    @api.expect(meal_form)
    def post(self):
        logging.info("meal received")        
        form = request.get_json()

        try:
            meal = validate_meal_form(form)
        except (KeyError, InvalidFormError) as err:
            return (error_model.represent_error(str(err)), 400)

        logging.info("Meal received, store")

        repository = get_meal_repository()

        repository.insert_meal(meal["date"].isoformat(), meal["start_week"], meal["meal_type"], meal["participants"], meal["meal"], meal["notes"])

        return ("Meal stored", 201)

    @api.doc('return last meal inserted')
    @api.response(200, 'Meal', model=meal_form)
    @api.response(400, 'Bad Request', model=error_model.error_view)
    @api.response(404, 'Not Found', model=error_model.error_view)
    def get(self):
        logging.info("Requested last meal")
        try:
            return(meal_model.represent_meal(get_meal_repository().get_last_meal()), 200)
        except KeyError as err:
            return(error_model.represent_error(str(err)), 404)
    
class InvalidFormError(Exception):
    pass