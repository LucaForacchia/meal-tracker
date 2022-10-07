from datetime import datetime, date
import pytest

from domain.meal import Meal

from infrastructure.persistence.meal_repository import MealRepository

from tests.utils import database, clean_db, get_meal

@pytest.fixture
def repository(database):
    (db, db_type) = database
    for table in ["meals"]:
        clean_db(db, table)
    return MealRepository(db, db_type)

@pytest.mark.repository
def test_init_db(database):
    # given: a valid db connection
    (db, db_type) = database

    # when: init the repo
    repo = MealRepository(db, db_type)

    # then: the db tables are created
    c = db.cursor()
    c.execute("SELECT * FROM  meals")
    # no error has being thrown, careful there are differences with mysql

@pytest.mark.repository
def test_save_meal(repository, database):
    # given: a correctly initialized repository and a valid meal:
    meal_obj = get_meal()

    # when: inserting a new meal in db
    repository.insert_meal(meal_obj)

    # then: the meal is correctly stored into the db
    (db, db_type) = database

    c = db.cursor()
    c.execute("SELECT * FROM meals")
    meals = c.fetchall()
    assert len(meals) == 1
    assert meals[0] == ('2022-01-01', 1641034800, 0, 'Pranzo', 'Entrambi', 'Test meal', 'TESTMEAL', 'Nota')

@pytest.mark.repository
def test_save_meal(repository, database):
    # given: a correctly initialized repository and a valid meal:
    meal_obj = get_meal()

    # when: inserting a new meal in db
    repository.insert_meal(meal_obj)

    # then: the meal is correctly stored into the db
    (db, db_type) = database

    c = db.cursor()
    c.execute("SELECT * FROM meals")
    meals = c.fetchall()
    assert len(meals) == 1
    assert meals[0] == ('2022-01-01', 1641034800, 0, 'Pranzo', 'Entrambi', 'Test meal', 'TESTMEAL', 'Nota')

@pytest.mark.repository
def test_save_meal_new_week(repository, database):
    # given: a correctly initialized repository and a valid meal:
    meal_obj = get_meal()
    meal_obj.start_week = True
    meal_obj.week_number = 120

    # when: inserting a new meal in db
    repository.insert_meal(meal_obj)

    # then: the meal is correctly stored into the db
    (db, db_type) = database

    c = db.cursor()
    c.execute("SELECT * FROM meals")
    meals = c.fetchall()
    assert len(meals) == 1
    assert meals[0] == ('2022-01-01', 1641034800, 120, 'Pranzo', 'Entrambi', 'Test meal', 'TESTMEAL', 'Nota')

@pytest.mark.repository
def test_get_last_meal(repository):
    # given: a meal inserted into db
    repository.insert_meal(get_meal())

    # when: requiring the last meal inserted:
    meal_object = repository.get_last_meal()

    # then: a meal_obj is retrieved
    assert type(meal_object) == Meal
    assert meal_object.date == "2022-01-01"
    assert meal_object.timestamp == 1641034800
    assert meal_object.meal_type == "Pranzo"
    assert meal_object.participants == "Entrambi"
    assert meal_object.meal == "Test meal"
    assert meal_object.notes == "Nota"
    assert not meal_object.start_week
    assert meal_object.week_number is None
    assert meal_object.meal_id == "TESTMEAL"

@pytest.mark.repository
def test_meal_counts(repository):
    # given: 4 meal inserted into db, 2 of them having same meal_id
    repository.insert_meal(get_meal())
    repository.insert_meal(get_meal(date_meal=datetime(2022,1,2)))
    repository.insert_meal(get_meal(date_meal=datetime(2022,1,3), meal="Another meal"))
    repository.insert_meal(get_meal(date_meal=datetime(2022,1,4), meal="Third meal"))

    # when: requiring the count of meals:
    meal_counts = repository.get_meals_count()

    # then: meal_counts is as expected
    print(meal_counts)
    assert type(meal_counts) == dict
    assert len(meal_counts) == 3
    assert 'ANOTHERMEAL' in meal_counts
    assert meal_counts['ANOTHERMEAL'] == ('Another meal', 1)
    assert 'TESTMEAL' in meal_counts
    assert meal_counts['TESTMEAL'] == ('Test meal', 2)