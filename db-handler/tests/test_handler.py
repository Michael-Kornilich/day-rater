from fastapi.testclient import TestClient
from importlib import import_module

app = import_module("db-handler").app
client = TestClient(app)

GetPayload = import_module("db-handler").GetPayload
CommitPayload = import_module("db-handler").CommitPayload

"""
No server needed to test, only pytest
The container however has to be running to run the tests

To test run
docker container exec --tty <container-id> python -m pytest
"""

# TODO: write the tests
class TestJSONModels:
    def test_get_payload(self):
        return
