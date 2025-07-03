# bridge to the fastapi
from fastapi.testclient import TestClient
from fastapi import HTTPException
from typing import Callable

# type enforcer
from pydantic import validate_call as enforce_types

# tested objects
from db_handler.db_handler import app
from db_handler.utility import (
    load_db,
    validate_columns,
    GetPayload,
    CommitPayload
)

# testing related
import pytest

microservice = TestClient(app)

"""
No server needed to test, only pytest
The container however has to be running to run the tests

To test run
docker container exec --tty db_handler python -m pytest -v --tb=line
"""


# TODO: fix the code / tests

@enforce_types
def check_factory(exp_status_code: int, exp_text: str) -> Callable[[HTTPException], bool]:
    """
    Factory for pytest.raises(check=...).
    Takes in the expected status code and the text which are expected to be in the error message
    :param exp_status_code: Expected status code
    :param exp_text: Expected error message
    :return: check function
    """

    # HTTPException's are not supported for type enforcement
    def check_error(err: HTTPException) -> bool:
        if err.status_code != exp_status_code:
            return False

        if exp_text not in err.detail:
            return False

        return True

    return check_error


class TestLoader:

    def test_on_empty_db(self):
        check = check_factory(204, "empty")

        with pytest.raises(HTTPException, check=check):
            load_db(path="/app/db_handler/tests/test_empty.csv")

    def test_bad_path(self):
        bad_path = "hello/world.csv"
        check = check_factory(500, "An error occurred while importing the database")

        with pytest.raises(HTTPException, check=check):
            load_db(path=bad_path)

    def test_skewed_db(self):
        check = check_factory(500, "An error occurred while importing the database")

        with pytest.raises(HTTPException, check=check):
            load_db(path="/app/db_handler/tests/test_skewed.csv")

    def test_non_csv(self):
        bad_path = "/app/db_handler/tests/non_csv"
        check = check_factory(500, "An error occurred while importing the database")

        with pytest.raises(HTTPException, check=check):
            load_db(path=bad_path)


# No need for data validator since the db will handle the type checking in the future

class TestColumnValidator:
    db_columns = ("a", "b", "c", "d")

    # GET tests

    def test_get_none_cols(self):
        model = GetPayload(user="me")
        validate_columns(model, self.db_columns)

    def test_get_empty_cols(self):
        model = GetPayload(user="me", columns=[])
        validate_columns(model, self.db_columns)

    def test_get_good_cols(self):
        model = GetPayload(user="me", columns=["a", "b", "d"])
        validate_columns(model, self.db_columns)

    def test_get_bad_cols(self):
        model = GetPayload(user="me", columns=["a", "e", "f"])
        check = check_factory(400, "Some columns in the payload are not in the database")

        with pytest.raises(HTTPException, check=check):
            validate_columns(model, self.db_columns)

    def test_get_superset_cols(self):
        model = GetPayload(user="me", columns=["a", "b", "c", "d", "e"])
        check = check_factory(400, "Some columns in the payload are not in the database")

        with pytest.raises(HTTPException, check=check):
            validate_columns(model, self.db_columns)

    def test_get_duplicate_cols(self):
        model = GetPayload(user="me", columns=["a", "b", "b", "c"])
        check = check_factory(400, "There are duplicates in the requested columns")

        with pytest.raises(HTTPException, check=check):
            validate_columns(model, self.db_columns)

    # POST tests

    def test_post_empty_cols(self):
        model = CommitPayload(user="me", datetime="2020-01-01", data={})
        check = check_factory(400, "Columns (data) are empty")

        with pytest.raises(HTTPException, check=check):
            validate_columns(model, self.db_columns)

    def test_post_good_cols(self):
        model = CommitPayload(user="me", datetime="2020-01-01", data={"a": "A", "c": "C", "d": "D"})
        validate_columns(model, self.db_columns)

    def test_post_bad_cols(self):
        model = CommitPayload(user="me", datetime="2020-01-01", data={"e": "E", "c": "C", "d": "D"})
        check = check_factory(400, "Some columns in the payload are not in the database")

        with pytest.raises(HTTPException, check=check):
            validate_columns(model, self.db_columns)

    def test_post_superset_cols(self):
        model = CommitPayload(user="me", datetime="2020-01-01", data={"a": "A", "b": "B", "c": "C", "d": "D", "e": "E"})
        check = check_factory(400, "Some columns in the payload are not in the database")

        with pytest.raises(HTTPException, check=check):
            validate_columns(model, self.db_columns)

    # QUESTION: how does fastapi handle duplicate JSON keys?
