# Network related
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# parsing related
from pandas import read_csv, DataFrame, concat

# typing related
from pydantic import validate_call
from typing import List, Dict, Optional, Sequence, Union

# for getting the db filepath
from os import environ

app = FastAPI()
PATH = environ["INTERNAL_DB_PATH"]


class GetPayload(BaseModel):
    user: str
    columns: Optional[List[str]] = None


class CommitPayload(BaseModel):
    user: str
    datetime: str
    data: Dict[str, Union[int, float, str]]


@validate_call
def validate_columns(payload: GetPayload | CommitPayload, columns: Sequence[str]) -> None:  # error in type enforcer
    """
    Incoming JSON validator. Checks columns
    Why: incorporating this into the Get | CommitPayload would bring over-proportional complexity

    :param payload: The incoming JSON object
    :param columns: Columns in the database
    :return: None
    :raises 400: if the payload is bad
    """
    if payload.columns is None:
        return

    if not set(payload.columns).issubset(columns):
        raise HTTPException(
            status_code=400,
            detail=f"Some columns in the payload are not in the database: {",".join(set(payload.columns).difference(columns))}"
        )


@validate_call
def load_db(path: str) -> DataFrame:
    """
    Import the database while checking its integrity and correctness

    :param path: Path to the db
    :return: pandas DataFrame of the database
    :raises 500: if the pandas import failed
    :raises 204: if the database file is empty
    """
    try:
        db = read_csv(path, index_col="datetime")
    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while importing the database:\n"
                   f"{type(err).__name__} - {err}"
        )

    if db.empty:
        raise HTTPException(status_code=204, detail=f"The database at {path} is empty")

    return db


@app.get("/get", status_code=200)
async def get_db(payload: GetPayload) -> Dict[str, list]:
    """
    Convert user's data into a json string.
    :param payload: The JSON payload with fields "user" and "columns"
    :return: a json like string with the following keys: columns, index, data.
    """
    db = load_db(PATH)
    validate_columns(payload, list(db.columns))

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
    validate_columns(payload, db.columns)

    new_row = DataFrame(payload.data, index=payload.index)
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
