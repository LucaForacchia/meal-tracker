from datetime import datetime, date
import pytest

from infrastructure.persistence.meal_repository import MealRepository

from tests.utils import database, clean_db

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
    # given: a correctly initialized repository
                        # date,
                        # start_week,
                        # type,
                        # participants,
                        # meal,
                        # notes
    # when: inserting a new meal in db
    repository.insert_meal(date(2022,4,29).isoformat(), False, "Pranzo", "Luca", "Carbonara", "Primo pasto inserito!")

    # then: the meal is correctly stored into the db
    (db, db_type) = database

    c = db.cursor()
    c.execute("SELECT * FROM meals")
    meals = c.fetchall()
    assert len(meals) == 1
    assert meals[0] == ("2022-04-29", 0, "Pranzo", "Luca", "Carbonara", "Primo pasto inserito!")