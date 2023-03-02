from datetime import datetime, date
import pytest

from domain.meal import Meal

from infrastructure.services.meal_service import MealService
from infrastructure.persistence.meal_repository import MealRepository

from tests.utils import database, clean_db, get_meal

@pytest.fixture
def service(database):
    (db, db_type) = database
    for table in ["meals"]:
        clean_db(db, table)
    return MealService(db, {"db_type": db_type})

@pytest.mark.service
def test_store_meal(service, database):
    # given: a meal service and a valid meal:
    meal_obj = get_meal()

    # when: inserting a new meal in db
    service.store_meal(meal_obj)

    # then: the meal is correctly stored into the db
    (db, db_type) = database

    c = db.cursor()
    c.execute("SELECT * FROM meals")
    meals = c.fetchall()
    assert len(meals) == 1
    assert meals[0] == ('2022-01-01', 1641034800, 0, 'Pranzo', 'Entrambi', 'Test meal', 'TESTMEAL', None, 'Nota')

@pytest.mark.service
def test_store_meal_new_week(service, database):
    # given: a meal service and a valid meal, with a week previously insertd into db:
    meal_obj = get_meal()
    meal_obj.start_week = True
    meal_obj.week_number = 120

    # when: inserting a new meal in db
    service.repository.insert_meal(meal_obj)

    new_meal = get_meal(date_meal=datetime(2022,2,15), start_week=True)

    # when: inserting a new meal in db
    service.store_meal(new_meal)

    # then: the meal is correctly stored into the db
    (db, db_type) = database

    c = db.cursor()
    c.execute("SELECT * FROM meals")
    meals = c.fetchall()
    print(meals)
    assert len(meals) == 2
    assert meals[0] == ('2022-01-01', 1641034800, 120, 'Pranzo', 'Entrambi', 'Test meal', 'TESTMEAL', None, 'Nota')
    assert meals[1] == ('2022-02-15', 1644922800, 121, 'Pranzo', 'Entrambi', 'Test meal', 'TESTMEAL', None, 'Nota')

@pytest.mark.service
def test_get_weekly_meals(service, database):
    # given: a meal service and valid meals, with week previously insertd into db:
    meal_obj = get_meal()
    meal_obj.start_week = True
    meal_obj.week_number = 120
    service.repository.insert_meal(meal_obj)
    new_meal = get_meal(date_meal=datetime(2022,2,15), start_week=True)
    service.store_meal(new_meal)
    new_meal = get_meal(date_meal=datetime(2022,2,16), start_week=True)
    service.store_meal(new_meal)

    # when: requiring last week meals (week number is None)
    weekly_meals = service.get_weekly_meals(None)

    # then: last week is retrieved correctly
    print(weekly_meals)
    assert weekly_meals[0] == 122
    assert len(weekly_meals[1]) == 1
    first_meal = weekly_meals[1][0] 
    assert type(first_meal) == Meal
    assert first_meal.date == "2022-02-16"
    assert first_meal.start_week == True
    assert first_meal.week_number is None

    # when: requiring previous week meals specifying week number
    weekly_meals = service.get_weekly_meals(121)

    # then: week meals are retrieved correctly
    print(weekly_meals)
    assert weekly_meals[0] == 121
    assert len(weekly_meals[1]) == 1
    first_meal = weekly_meals[1][0] 
    assert type(first_meal) == Meal
    assert first_meal.date == "2022-02-15"
    assert first_meal.start_week == True
    assert first_meal.week_number is None

    # when: requiring last week meals specifying week number
    weekly_meals = service.get_weekly_meals(122)

    # then: last week is retrieved correctly
    print(weekly_meals)
    assert weekly_meals[0] == 122
    assert len(weekly_meals[1]) == 1
    first_meal = weekly_meals[1][0] 
    assert type(first_meal) == Meal
    assert first_meal.date == "2022-02-16"
    assert first_meal.start_week == True
    assert first_meal.week_number is None
