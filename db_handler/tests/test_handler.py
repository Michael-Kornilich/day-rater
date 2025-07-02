# bridge to the fastapi
from fastapi.testclient import TestClient
from fastapi import HTTPException

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
docker container exec --tty db_handler python -m pytest
"""

# TODO: more extensive testing of the loader
# + skewed db, not .csv files
class TestLoader:
    def test_on_empty_db(self):
        def check_error(err: HTTPException) -> bool:
            if err.status_code != 204:
                return False

            if "empty" not in err.detail:
                return False

            return True

        with pytest.raises(HTTPException, check=check_error):
            load_db(path="/app/db_handler/tests/test_mock_empty_db.csv")

    def test_bad_path(self):
        bad_path = "hello/world.csv"

        def check_error(err: HTTPException) -> bool:
            print(err.status_code, err.detail)
            if err.status_code != 500:
                return False

            if "An error occurred while importing the database" not in err.detail:
                return False

            return True

        with pytest.raises(HTTPException, check=check_error):
            load_db(path=bad_path)

# TODO: test the data validator
# number of columns, SQL injections?, data type validation

# TODO: test the column validator