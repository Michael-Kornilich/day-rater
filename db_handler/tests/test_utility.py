# bridge to the fastapi
from fastapi import HTTPException

# typing
from typing import Callable

# type enforcer
from pydantic import validate_call as enforce_types

# tested objects
from db_handler.utility import (
    load_db,
    validate_columns,
    validate_post_data,
    GetPayload,
    CommitPayload
)

# testing related
import pytest
from random import sample

"""
No server needed to test, only pytest
The container however has to be running to run the tests

To test run
docker container exec --tty db_handler pytest -v --tb=line
"""


@enforce_types
def check_factory(exp_status_code: int, exp_text: str | None = None) -> Callable[[HTTPException], bool]:
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

        if exp_text and (exp_text not in err.detail):
            return False

        return True

    return check_error


class TestLoader:

    def test_on_empty_db(self):
        check = check_factory(204, "empty")

        with pytest.raises(HTTPException, check=check):
            load_db(path="/app/db_handler/tests/test_files/test_empty.csv")

    def test_bad_path(self):
        bad_path = "hello/world.csv"
        check = check_factory(500, "An error occurred while importing the database")

        with pytest.raises(HTTPException, check=check):
            load_db(path=bad_path)

    def test_skewed_db(self):
        check = check_factory(500, "An error occurred while importing the database")

        with pytest.raises(HTTPException, check=check):
            load_db(path="/app/db_handler/tests/test_files/test_skewed.csv")

    def test_non_csv(self):
        bad_path = "/app/db_handler/tests/test_files/non_csv"
        check = check_factory(500, "An error occurred while importing the database")

        with pytest.raises(HTTPException, check=check):
            load_db(path=bad_path)


# No need for data validator since the db will handle the type checking in the future
class TestColumnValidator:
    db_columns = ("a", "b", "c", "d", "e", "f", "g")

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
        model = GetPayload(user="me", columns=["a", "x", "f"])
        check = check_factory(400, "Some columns in the payload are not in the database")

        with pytest.raises(HTTPException, check=check):
            validate_columns(model, self.db_columns)

    def test_get_superset_cols(self):
        model = GetPayload(user="me", columns=["a", "b", "c", "d", "e", "x", "y"])
        check = check_factory(400, "Some columns in the payload are not in the database")

        with pytest.raises(HTTPException, check=check):
            validate_columns(model, self.db_columns)

    def test_get_duplicate_cols(self):
        model = GetPayload(user="me", columns=["a", "b", "b", "c"])
        check = check_factory(400, "There are duplicates in the requested columns")

        with pytest.raises(HTTPException, check=check):
            validate_columns(model, self.db_columns)

    def test_get_100_good_random(self):
        for _ in range(100):
            model = GetPayload(user="me", columns=sample(self.db_columns, k=4))
            validate_columns(model, self.db_columns)

    def test_get_100_bad_random(self):
        check = check_factory(400, "Some columns in the payload are not in the database")

        for _ in range(100):
            model = GetPayload(user="me", columns=sample(["x", "y", "z", "1", "2", "3", "4"], k=4))
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
        model = CommitPayload(user="me", datetime="2020-01-01", data={"x": "X", "c": "C", "d": "D"})
        check = check_factory(400, "Some columns in the payload are not in the database")

        with pytest.raises(HTTPException, check=check):
            validate_columns(model, self.db_columns)

    def test_post_superset_cols(self):
        model = CommitPayload(user="me", datetime="2020-01-01", data={"a": "A", "b": "B", "c": "C", "d": "D", "x": "X"})
        check = check_factory(400, "Some columns in the payload are not in the database")

        with pytest.raises(HTTPException, check=check):
            validate_columns(model, self.db_columns)

    # QUESTION: how does fastapi handle duplicate JSON keys?

    def test_post_100_good_random(self):
        for _ in range(100):
            model = CommitPayload(
                user="me",
                datetime="2020-01-01 20:30:00",
                data={k: v for k, v in zip(sample(self.db_columns, k=4), [1, 2, 3, 4])}
            )
            validate_columns(model, self.db_columns)

    def test_post_100_bad_random(self):
        check = check_factory(400, "Some columns in the payload are not in the database")

        for _ in range(100):
            model = CommitPayload(
                user="me",
                datetime="2020-01-01 20:30:00",
                data={k: v for k, v in zip(sample(["x", "y", "z", "1", "2", "3", "4"], k=4), [1, 2, 3, 4])}
            )
            with pytest.raises(HTTPException, check=check):
                validate_columns(model, self.db_columns)


# No need to test None values, since CommitPayload handles them
class TestCommitDataValidator:
    def test_bad_index(self):
        model = CommitPayload(user="me", datetime="hello world", data={"a": "A", "b": "B"})
        check = check_factory(400, "Bad index")

        with pytest.raises(HTTPException, check=check):
            validate_post_data(model)

    def test_good_index(self):
        model = CommitPayload(user="me", datetime="2020-01-01 20:00:00", data={"a": "A", "b": "B"})
        validate_post_data(model)

    def test_no_data(self):
        model = CommitPayload(user="me", datetime="2020-01-01 20:00:00", data={})
        check = check_factory(400, "No data to commit")

        with pytest.raises(HTTPException, check=check):
            validate_post_data(model)

    def test_everything_good(self):
        model = CommitPayload(user="me", datetime="2020-01-01 20:00:00", data={"a": "A", "b": "B"})
        validate_post_data(model)
