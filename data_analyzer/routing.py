# Server related
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request
import httpx

# parsing & IO
from pandas import DataFrame

app = FastAPI()

# TODO: figure out how to transfer files (graphics)

def get_data(user: str) -> DataFrame:
    """
    Import the data from the database
    :param user: the username
    :return: pandas.DataFrame of the data
    :raises HTTPException: If the import of the database failed
    """
    response = httpx.post("http://db_handler/get", json={"user": user}) # TODO: not sure if this works
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Connecting to the database failed: {response.json()}")

    raw_data = response.json()
    try:
        data = DataFrame(
            raw_data["data"],
            index=raw_data["index"],
            columns=raw_data["columns"]
        )
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Failed to import the data from the database:"
                                                    f"\t{type(err).__name__} - {err}")

    return data


# Override the default handler for pydantic ValidationError's
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    err_dict = exc.errors()[0]
    where = err_dict["loc"]
    detail = {"msg": err_dict["msg"], "got": err_dict["input"]}
    return JSONResponse(content={"loc": where, "detail": detail}, status_code=400)


@app.get("/analyse", status_code=200)
async def analyse(user: str) -> dict:
    data = get_data(user)
    return {"status": "analyzed", "database": data.shape}


@app.get("/healthcheck", status_code=200)
async def heath_check_db() -> int:
    """
    Do a db healthcheck by importing it
    :return: 200 if success
    :raises 500, 204: same as load_db
    """
    return 200
