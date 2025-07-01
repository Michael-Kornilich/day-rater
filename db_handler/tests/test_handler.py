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


# TODO: write the tests
def test_loader_empty_db():
    def check_status_code(err: HTTPException) -> bool:
        return True if err.status_code == 204 else False

    with pytest.raises(HTTPException, check_status_code):
        load_db(path="test_mock_empty_db.csv")
