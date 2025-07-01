# bridge to the fastapi
from fastapi.testclient import TestClient
from fastapi import HTTPException

# module imported
from importlib import import_module

# testing related
import pytest

app = import_module("db_handler").app
client = TestClient(app)

GetPayload = import_module("db_handler").GetPayload
CommitPayload = import_module("db_handler").CommitPayload
load_db = import_module("utility.py").load_db
validate_post_columns = import_module("utility.py").validate_post_columns
validate_get_columns = import_module("utility.py").validate_get_columns

"""
No server needed to test, only pytest
The container however has to be running to run the tests

To test run
docker container exec --tty <container-id> python -m pytest
"""


# TODO: write the tests
def test_loader():
    payload = GetPayload(user=15, columns=["hello", "world"])
