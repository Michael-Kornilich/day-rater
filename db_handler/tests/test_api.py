# bridge to the API
from fastapi.testclient import TestClient
from db_handler.db_handler import app

# testing related
import pytest

# debug variables
from os import environ

"""
No server needed to test, only pytest
The container however has to be running to run the tests

To test run
docker container exec --tty db_handler pytest /app/db_handler/tests/test_api.py -vv --tb=line
"""

client = TestClient(app)


# pydantic validate_call does not handle the Response object
def parse_response(response) -> str:
    return (f"\nStatus code: {response.status_code}\n"
            f"Headers: \n\t{response.headers}\n"
            f"Body: \n\t{response.json()}\n")


def test_bad_path():
    response = client.request("GET", "/bad_path")
    if response.status_code < 400:
        pytest.fail(f"Bad path accepted although should have not. {parse_response(response)}")


def test_healthcheck():
    response = client.request("GET", "/healthcheck")
    if response.status_code != 200:
        pytest.fail(f"Healthcheck failed: {parse_response(response)}")


class TestGetDB:
    # why .request and not .get => .get does not support (json) body in the request
    def test_good_request(self):
        response = client.request(
            "GET",
            "/get",
            json={"user": "me"}
        )
        assert response.status_code == 200, f"Good request failed: {parse_response(response)}"

    def test_wrong_keys(self):
        response = client.request(
            "GET",
            "/get",
            json={"user": "me", "hello": "hello world"}
        )
        assert response.status_code != 200, f"Expected rejection, got {parse_response(response)}"

    def test_empty_columns(self):
        response = client.request(
            "GET",
            "/get",
            json={"user": "me", "columns": []}
        )
        assert response.status_code == 200, f"Expected success, got {parse_response(response)}"

    def test_bad_column_values(self):
        response = client.request(
            "GET",
            "/get",
            json={"user": "me", "columns": ["xy", "zh"]}
        )
        assert response.status_code != 200, f"Expected rejection, got {parse_response(response)}"


class TestCommitDB:
    @classmethod
    def setup_class(cls):
        environ["DEBUG"] = "True"

    def test_wrong_keys(self):
        response = client.request("GET", "/commit", json={
            "user": "me",
            "datetime": "2020-05-01 20:30:45",
            "odd_key": ["hello", "world"],
            "data": {"day_rank": 8}
        })
        assert response.status_code == 400, f"Expected rejection, got {parse_response(response)}"

    def test_empty_data(self):
        response = client.request("POST", "/commit", json={
            "user": "me",
            "datetime": "2020-05-01 20:30:45",
            "data": {}
        })
        assert response.status_code == 400, f"Expected rejection, got {parse_response(response)}"

    def test_bad_column_values(self):
        response = client.request("POST", "/commit", json={
            "user": "me",
            "datetime": "2020-05-01 20:30:45",
            "data": {"bad_column": 8, "temperature": 25}
        })
        assert response.status_code == 400, f"Expected success, got {parse_response(response)}"

    def test_good_request(self):
        response = client.request("POST", "/commit", json={
            "user": "me",
            "datetime": "2020-05-01 20:30:45",
            "data": {"day_rank": 8, "temperature": 25}
        })
        assert response.status_code == 201, f"Expected success, got {parse_response(response)}"

    @classmethod
    def teardown_class(cls):
        environ["DEBUG"] = "False"
