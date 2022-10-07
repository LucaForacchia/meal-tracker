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
    assert meals[0] == ('2022-01-01', 1641034800, 0, 'Pranzo', 'Entrambi', 'Test meal', 'TESTMEAL', 'Nota')

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
    assert meals[0] == ('2022-01-01', 1641034800, 120, 'Pranzo', 'Entrambi', 'Test meal', 'TESTMEAL', 'Nota')
    assert meals[1] == ('2022-02-15', 1644922800, 121, 'Pranzo', 'Entrambi', 'Test meal', 'TESTMEAL', 'Nota')