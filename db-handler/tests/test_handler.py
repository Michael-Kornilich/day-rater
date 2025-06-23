from fastapi.testclient import TestClient
from importlib import import_module

app = import_module("db-handler").app

client = TestClient(app)

# No server needed to test, only pytest

