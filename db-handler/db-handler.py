# Network related
from fastapi import FastAPI

# parsing related
from pandas import DataFrame, concat

# typing related
from typing import Dict

# for getting the db filepath
from os import environ

# utility functions
from utility import (
    GetPayload,
    CommitPayload,
    validate_get_columns,
    validate_post_columns,
    load_db
)

app = FastAPI()
PATH = environ["INTERNAL_DB_PATH"]


@app.get("/get", status_code=200)
async def get_db(payload: GetPayload) -> Dict[str, list]:
    """
    Convert user's data into a json string.
    :param payload: The JSON payload with fields "user" and "columns"
    :return: a json like string with the following keys: columns, index, data.
    """
    db = load_db(PATH)
    validate_get_columns(payload, tuple(db.columns))

    # in the payload the columns are optional
    columns = payload.columns or db.columns

    return db.loc[:, columns].to_dict(orient="split")  # error: invalid dict


# Not async to avoid race conditions
@app.post("/commit", status_code=201)
def commit_db(payload: CommitPayload) -> None:
    """
    Commit a change into the database
    :param payload: JSON as per the docs.md
    :return: 201 if success
    :raises 400, 500, 204: Same as load_db and validate_columns
    """
    db = load_db(PATH)
    validate_post_columns(payload, tuple(db.columns))

    new_row = DataFrame(payload.data, index=[payload.datetime])
    db = concat([db, new_row])
    db.to_csv(PATH)
    return


@app.get("/healthcheck", status_code=200)
async def heath_check_db() -> None:
    """
    Do a db healthcheck by importing it
    :return: 200 if success
    :raises 500, 204: same as load_db
    """
    load_db(PATH)
    return
