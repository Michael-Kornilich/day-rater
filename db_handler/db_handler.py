# Server related
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request

# parsing & IO
from pandas import DataFrame, concat

# typing related
from typing import Dict

# for getting the db filepath
from os import environ

# utility functions / objects
from db_handler.utility import (
    GetPayload,
    CommitPayload,
    validate_get_columns,
    validate_post_columns,
    validate_post_data,
    load_db
)

app = FastAPI()
PATH = environ["INTERNAL_DB_PATH"]


# Override the default handler for pydantic ValidationError's
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    err_dict = exc.errors()[0]
    where = err_dict["loc"]
    detail = {"msg": err_dict["msg"], "got": err_dict["input"]}
    return JSONResponse(content={"loc": where, "detail": detail}, status_code=400)


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

    return db.loc[:, columns].to_dict(orient="split")


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
    validate_post_data(payload, db)

    new_row = DataFrame(payload.data, index=[payload.datetime])
    db = concat([db, new_row])
    db.to_csv(PATH, index=True, index_label="datetime")
    return


@app.get("/healthcheck", status_code=200)
async def heath_check_db() -> dict:
    """
    Do a db healthcheck by importing it
    :return: 200 if success
    :raises 500, 204: same as load_db
    """
    db = load_db(PATH)
    return {"columns": len(db.columns), "rows": len(db)}
