import csv
from datetime import datetime, date
import requests
import argparse
import subprocess
import warnings
import json
from time import sleep


def write_db_entry(entry: dict, path: str, na_convention: str = "None") -> None:
    """
    Write a row into a .csv file.
    :param path: Pathlike or a string path to the database file
    :param entry: Dictionary with the data to be written. Keys which are in the db but not in the data will be filled with "None"
    :param na_convention: How to write nonexistent into the database
    :return: None
    :raises TypeError: if the path is not a string or if the file is not a .csv file
    """
    if not isinstance(na_convention, str): raise TypeError(
        f"Na convention must be a string, {type(na_convention)} passed.")
    if not isinstance(path, str): raise TypeError(f"Path must be a string, {type(path)} passed.")
    if v := path.split(".")[-1] != "csv": raise TypeError(f"File must be a csv file, got .{v} instead")

    columns: tuple = get_columns(path)

    if v := set(entry.keys()) - set(columns):
        warnings.warn(f"New columns have been passed that are not in the database: {v}."
                      f"Ignoring the columns.", category=RuntimeWarning)

    # Checking whether there is a newline at the end of the file
    with open(path, mode="rb+") as file:
        file.seek(-1, 2)
        if file.read() != b"\n":
            file.write(b"\n")

    _dict = {column: entry.get(column, na_convention) for column in columns}
    with open(path, mode="a", newline="\n") as file:
        writer_ = csv.DictWriter(file, fieldnames=columns)
        writer_.writerow(_dict)


def get_columns(path: str) -> tuple:
    """
    Parse column names of a csv file.
    :param path: Pathlike object of a string path to the database file
    :return: Columns / header of a csv file
    :raises TypeError: if the path is not a string or if the file prefix is not .csv
    """
    if not isinstance(path, str): raise TypeError(f"Path must be a string, {type(path)} passed.")
    if v := path.split(".")[-1] != "csv": raise TypeError(f"File must be a csv file, got .{v} instead")

    import re
    with open(path) as file:
        raw_data = file.readline()
        li = re.findall(r"[a-zA-Z0-9_-]+", raw_data)
        return tuple(li)


def get_season(dt: date | datetime) -> str:
    """
    Get a season of the year from a datetime object.
    :param dt: python datetime object, or any object that defines .month (-> int) attribute
    :return: winter | spring | summer | autumn
    :raises TypeError: if the passed object is invalid
    :raises ValueError: if the month not in [1;12]
    """
    if not isinstance(dt, (date, datetime)) and not hasattr(dt, "month"):
        raise TypeError("The dt object must be a date or a datetime or define a month attribute")

    month = dt.month
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "autumn"
    else:
        raise ValueError(f"Invalid month {month}")


def load_json(path: str) -> dict:
    """
    Unlike json.load(), this function only requires a path to parse a json into a dictionary
    :param path: string path
    :return: json as python dictionary
    :raises ImportError: if the parsing failed
    """
    if not isinstance(path, str):
        raise TypeError(f"path must be a string, {type(path)} passed.")

    with open(path, mode="r") as f:
        try:
            dict_ = json.load(f)
        except Exception as err:
            raise ImportError(f"An error occurred while parsing a json file:\n"
                              f"{type(err).__name__}\n"
                              f"\t{err}")
    return dict_


def request_json(url: str, metaname: str, tp: str = "GET", attempts: int = 3, wait: float | int = 5) -> dict:
    """
    Sends an url request with expectation of a json return value.
    :param url: the (fully loaded) url to send request to
    :param metaname: the name of the api service to display in warning messages
    :param tp: type of the request to send: GET, POST, UPDATE...
    :param attempts: Number of attempts to make before giving up. Must be >= 1
    :param wait: Number of seconds to wait before making the next request. Must be >= 1
    :return: json as python dictionary
    """
    if not isinstance(url, str): raise TypeError(f"URL, must be a string, {type(url)} passed.")
    if not isinstance(metaname, str): raise TypeError(f"Metaname, must be a string, {type(metaname)} passed.")
    if not isinstance(tp, str): raise TypeError(f"Request type, must be a string, {type(tp)} passed.")
    if not hasattr(requests, tp.lower()): raise ValueError(f"Request type {tp} is invalid.")
    if not isinstance(attempts, int): raise TypeError(f"Number of attempts must be an int, {type(attempts)} passed.")
    if attempts < 1: raise ValueError(f"The number of call attempts must be >= 1, {attempts} passed.")
    if not isinstance(wait, (int, float)): raise TypeError(f"The wait time must be a number, {type(wait)} passed.")
    if wait < 1: raise ValueError("The wait time must be >= 1 (seconds).")

    for i in range(attempts):
        response = getattr(requests, tp.lower())(url)
        if response.ok: break

        warning = "Error calling the {what} API ({code}){again}.".format(
            code=response.status_code,
            what=metaname,
            again=" trying again.." if i < attempts - 1 else ""
        )
        warnings.warn(warning, category=RuntimeWarning)
        sleep(wait)

    try:
        dict_ = response.json()
        return dict_
    except requests.exceptions.JSONDecodeError:
        warnings.warn("{what} API's response does not contain a valid json.".format(what=metaname))
        return dict()


if __name__ != "__main__":
    quit()

parser = argparse.ArgumentParser()
parser.add_argument(
    "--day-rank", "-d",
    type=int,
    default=-1,
    choices=list(range(1, 11)),
    dest="day_rank",
    metavar="ranking"
)
parser.add_argument(
    "--analyze", "-a",
    action="store_true",
    dest="analyze"
)
args = vars(parser.parse_args())

day_rank = args["day_rank"]
analyze = args["analyze"]

if day_rank != -1:
    secrets = load_json("secrets.json")

    loaded_url = (
        "https://api.tomorrow.io/v4/weather/realtime?location={location}&units=metric&apikey={apikey}"
        .format(location=",".join(map(str, secrets["location"])), apikey=secrets["apikey"])
    )

    res = request_json(
        url=loaded_url,
        tp="GET",
        metaname="weather"
    )
    if res.items():
        weather_data = res["data"]["values"]
    else:
        weather_data = dict()

    datetime_now: datetime = datetime.now()
    entry = {
        # magnetic_activity, dusk, dawn
        "datetime": datetime_now.strftime("%Y-%m-%d %H:%M:%S"),
        "day_rank": day_rank,
        "season": get_season(datetime_now),
        "temperature": weather_data.get("temperature"),
        "cloud_cover": weather_data.get("cloudCover"),
        "humidity": weather_data.get("humidity"),
        "atm_pressure": weather_data.get("pressureSurfaceLevel"),
        "wind_speed": weather_data.get("windSpeed"),
        "wind_direction": weather_data.get("windDirection"),
        "feels_like": weather_data.get("temperatureApparent"),
        "rain_intensity": weather_data.get("rainIntensity"),
        "sleet_intensity": weather_data.get("sleetIntensity"),
        "snow_intensity": weather_data.get("snowIntensity")
    }
    write_db_entry(entry, "db.csv")

if analyze:
    print("Calling the analyzer script...")
    analyzer_subprocess = subprocess.run(['python', 'data-analyzer.py'], capture_output=True)
    print(f"{analyzer_subprocess.returncode=}\n{analyzer_subprocess.stderr}\n{analyzer_subprocess.stdout}")
