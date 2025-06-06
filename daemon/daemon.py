from datetime import datetime, date

# API related
import requests
import json
from time import sleep

# process related
import subprocess
import warnings
import argparse


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


def request_json(url: str, metaname: str, tp: str = "GET", attempts: int = 3, wait: float | int = 5, **kwargs) -> dict:
    """
    Sends an url request with expectation of a json return value.
    :param url: the (fully loaded) url to send request to
    :param metaname: the name of the api service to display in warning messages
    :param tp: type of the request to send: GET, POST, UPDATE...
    :param attempts: Number of attempts to make before giving up. Must be >= 1
    :param wait: Number of seconds to wait before making the next request. Must be >= 1
    :param kwargs: keyword arguments to pass to requests
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
        response = getattr(requests, tp.lower())(url, **kwargs)
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
    default=0,
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

secrets = load_json("secrets.json")
loaded_url = (
    "https://api.tomorrow.io/v4/weather/history/recent?timesteps={timestep}&location={location}&units=metric&apikey={apikey}"
    .format(timestep="1d", location=",".join(map(str, secrets["location"])), apikey=secrets["apikey"])
)

if day_rank:
    res = request_json(
        url=loaded_url,
        tp="GET",
        metaname="weather"
    )

    if res.items():
        weather_data = res["timelines"]["daily"][1]["values"]
    else:
        weather_data = dict()

    datetime_now: datetime = datetime.now()
    entry = {
        # magnetic_activity
        "datetime": datetime_now.strftime("%Y-%m-%d %H:%M:%S"),
        "day_rank": day_rank,
        "sunrise": weather_data["sunriseTime"].replace("T", " ").replace("Z", ""),
        "sunset": weather_data["sunsetTime"].replace("T", " ").replace("Z", ""),
        "season": get_season(datetime_now),
        "temperature": weather_data.get("temperatureAvg"),
        "cloud_cover": weather_data.get("cloudCoverAvg"),
        "humidity": weather_data.get("humidityAvg"),
        "atm_pressure": weather_data.get("pressureSurfaceLevelAvg"),
        "wind_speed": weather_data.get("windSpeedAvg"),
        "wind_direction": weather_data.get("windDirectionAvg"),
        "feels_like": weather_data.get("temperatureApparentAvg"),
        "rain_intensity": weather_data.get("rainIntensityAvg"),
        "sleet_intensity": weather_data.get("sleetIntensityAvg"),
        "snow_intensity": weather_data.get("snowIntensityAvg")
    }
    # call db-handler with the entry json

if analyze:
    # call analyzer
    print("Calling the analyzer script...")
    analyzer_subprocess = subprocess.run(['python', 'data-analyzer.py'], capture_output=True)
    print(f"{analyzer_subprocess.returncode=}\n{analyzer_subprocess.stderr}\n{analyzer_subprocess.stdout}")
