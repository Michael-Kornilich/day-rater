# bridge to the API
from fastapi.testclient import TestClient
from fastapi import HTTPException
from db_handler.db_handler import app

# testing related
import pytest

client = TestClient(app)


def test_bad_path():
    pass


class TestGetDB:
    def test_wrong_keys(self):
        pass

    def test_empty_columns(self):
        pass

    def test_bad_column_values(self):
        pass

    def test_good_request(self):
        pass


class TestCommitDB:
    def test_wrong_keys(self):
        pass

    def test_empty_columns(self):
        pass

    def test_bad_column_values(self):
        pass

    def test_good_request(self):
        pass
