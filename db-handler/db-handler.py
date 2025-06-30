# Network related
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict

# parsing related
from pandas import read_csv, DataFrame, concat

# typing related
from type_enforced import Enforcer

app = FastAPI()
PATH = "/db/db.csv"


class GetPayload(BaseModel):
    user: str
    columns: List[str] | None = None


class CommitPayload(BaseModel):
    user: str
    data: Dict[str, str]


@Enforcer
def validate_columns(payload: GetPayload | CommitPayload, columns: List[str]) -> None:  # error in type enforcer
    """
    Check that the columns in the payload are in the database
    :param payload:
    :param columns:
    :return:
    """
    # datetime is not a column, but an index
    # should change the structure, where the index is sent separately
    if not set(payload.columns).issubset(columns):
        raise HTTPException(
            status_code=400,
            detail=f"Some columns in the payload are not in the database: {",".join(set(payload.columns).difference(columns))}"
        )


@Enforcer
def load_db(path: str) -> DataFrame:
    """
    Import the database while checking its integrity and correctness
    :param path: Path to the db
    :return: pandas DataFrame of the database
    :raises 500, 204, 404:
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
async def get_db(payload: GetPayload) -> dict:
    """
    Convert user's data into a json string.
    :param payload: The JSON payload with fields "user" and "columns"
    :return: a json like string with the following keys: columns, index, data.
    """
    db = load_db(PATH)
    validate_columns(payload, list(db.columns))

    return db.loc[:, payload.columns].to_json(orient="split")


@app.post("/commit", status_code=201)
def commit_db(payload: CommitPayload) -> None:
    """
    Commit a change into the database
    :param payload: JSON as per the docs.md
    :return: 201
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
    """
    load_db(PATH)
    return
