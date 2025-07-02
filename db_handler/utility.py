# Network related
from fastapi import HTTPException
from pydantic import BaseModel

# parsing related
from pandas import read_csv, DataFrame

# typing related
from pydantic import validate_call as enforce_types
from typing import List, Dict, Optional, Tuple, Union


class GetPayload(BaseModel):
    user: str
    columns: Optional[List[str]] = None


class CommitPayload(BaseModel):
    user: str
    datetime: str
    data: Dict[str, Union[int, float, str]]


@enforce_types
def validate_get_columns(payload: GetPayload, db_columns: Tuple[str, ...]) -> None:
    """
    Incoming JSON validator. Cross validates incoming columns with the ones in the database
    Why: incorporating this into the GetPayload would bring over-proportional complexity

    :param payload: The incoming JSON object
    :param db_columns: Columns in the database
    :return: None
    :raises 400: if the payload is bad
    """
    if payload.columns is None:
        return

    if len(payload.columns) != set(payload.columns):
        raise HTTPException(
            status_code=400,
            detail=f"There are duplicates in the requested columns: {",".join(payload.columns)}"
        )

    if not set(payload.columns).issubset(db_columns):
        raise HTTPException(
            status_code=400,
            detail=f"Some columns in the payload are not in the database: {",".join(set(payload.columns).difference(db_columns))}"
        )


@enforce_types
def validate_post_columns(payload: CommitPayload, columns: Tuple[str, ...]) -> None:
    """
    Incoming JSON validator. Cross validates incoming columns with the ones in the database
    Why: incorporating this into the CommitPayload would bring over-proportional complexity

    :param payload: The incoming JSON object
    :param columns: Columns in the database
    :return: None
    :raises 400: if the payload is bad
    """
    if not set(payload.data.keys()).issubset(columns):
        raise HTTPException(
            status_code=400,
            detail=f"Some columns in the payload are not in the database: {",".join(set(payload.columns).difference(columns))}"
        )


@enforce_types
def validate_post_data(payload: CommitPayload, db: DataFrame) -> None:
    # checking index
    from datetime import datetime
    try:
        datetime.strptime(payload.datetime, "%Y-%m-%d %H:%M:%S")
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail=f"{type(err).__name__} - {err}"
        )

    if not payload.data:
        raise HTTPException(
            status_code=400,
            detail="No data to commit"
        )

    # raise if any value is None or similar
    if not all(map(bool, payload.data.values())):
        raise HTTPException(
            status_code=400,
            detail="Some values are None"
        )


@enforce_types
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
