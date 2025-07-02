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
    validate_get_columns,
    validate_post_columns,
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
docker container exec --tty db_handler python -m pytest -v
"""


class TestLoader:
    @classmethod
    @enforce_types
    def check_factory(cls, s_code: int, text: str) -> Callable[[HTTPException], bool]:
        """
        pytest.raises(check=) function factory.
        Takes in the expected status code and the text are not satisfied
        :param s_code:
        :param text:
        :return:
        """

        # HTTPException's are not supported for type enforcement
        def check_error(err: HTTPException) -> bool:
            if err.status_code != s_code:
                return False

            if text not in err.detail:
                return False

            return True

        return check_error

    def test_on_empty_db(self):
        check = self.check_factory(204, "empty")

        with pytest.raises(HTTPException, check=check):
            load_db(path="/app/db_handler/tests/test_empty.csv")

    def test_bad_path(self):
        bad_path = "hello/world.csv"
        check = self.check_factory(500, "An error occurred while importing the database")

        with pytest.raises(HTTPException, check=check):
            load_db(path=bad_path)

    def test_skewed_db(self):
        check = self.check_factory(500, "An error occurred while importing the database")

        with pytest.raises(HTTPException, check=check):
            load_db(path="/app/db_handler/tests/test_skewed.csv")

    def test_non_csv(self):
        bad_path = "/app/db_handler/tests/non_csv"
        check = self.check_factory(500, "An error occurred while importing the database")

        with pytest.raises(HTTPException, check=check):
            load_db(path=bad_path)

# TODO: test the data validator
#   number of columns
#   SQL injections?
#   data type validation

# TODO: test the column validator

# TODO: add testing for GET

# TODO: add testing for POST

