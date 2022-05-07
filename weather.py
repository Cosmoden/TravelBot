import json

from requests import get
from datetime import datetime


def current_weather(lon, lat):
    with open("weather_key.txt", 'r') as f:
        key = f.read()
    url = "https://api.openweathermap.org/data/2.5/onecall"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": key,
        "exclude": "minutely,hourly,daily,alerts",
        "units": "metric",
        "lang": "ru",
    }
    response = get(url, params=params)
    data = response.json()["current"]
    return f""" {data["weather"][0]["description"].capitalize()}
    Температура воздуха {data["temp"]}°C
    Ощущается как {data["feels_like"]}°C
    Влажность {data["humidity"]}%"""


def forecast(lon, lat):
    with open("weather_key.txt", 'r') as f:
        key = f.read()
    url = "https://api.openweathermap.org/data/2.5/onecall"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": key,
        "exclude": "current,minutely,hourly,alerts",
        "units": "metric",
        "lang": "ru"
    }
    response = get(url, params=params).json()
    data = response["daily"]
    return "".join(f"""{str(datetime.now())[:10]}\n
        {day["weather"][0]["description"].capitalize()}
        Температура воздуха: днем {day["temp"]["day"]}°C, ночью {day["temp"]["night"]}
        Ощущается: днем как {day["feels_like"]["day"]}°C, ночью как {day["feels_like"]["night"]}
        Влажность {day["humidity"]}%\n\n""" for day in data)
