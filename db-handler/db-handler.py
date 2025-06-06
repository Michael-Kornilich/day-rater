# API Endpoint related
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# parsing related
from datetime import datetime
import pandas as pd

app = FastAPI()


class EntryTemplate(BaseModel):
    index: str
    data: dict


@app.get("/", status_code=200)
async def get_db():
    path = "db.csv"
    try:
        db = pd.read_csv(path, index_col="datetime")
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"An error occurred while importing the data base:\n"
                                                    f"{type(err).__name__} - {err}")

    return db.to_json(orient="split")


@app.post("/", status_code=201)
async def post_db(payload: EntryTemplate):
    path = "db.csv"
    try:
        db = pd.read_csv(path)
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"An internal exception has occurred:\n"
                                                    f"{type(err).__name__} - {err}")
    try:
        # ensure correct formating
        datetime.strptime(payload["index"], "%Y-%m-%d %H:%M:%S")
        new_row = pd.DataFrame(payload["data"], index=payload["index"])
    except Exception as err:
        raise HTTPException(status_code=400, detail="Bad JSON:\n"
                                                    f"{type(err).__name__} - {err}")

    db = pd.concat([db, new_row])
    db.to_csv(path)
    return
