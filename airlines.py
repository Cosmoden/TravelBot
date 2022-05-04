import json

from requests import get, post


def get_flights(origin, dest, date):
    travelpayouts_url = "http://autocomplete.travelpayouts.com/places2"
    params1 = {
        "term": origin,
        "locale": "ru",
        "types[]": "city"
    }
    response1 = get(travelpayouts_url, params=params1).json()
    code1 = response1[0]["code"]
    params2 = {
        "term": dest,
        "locale": "ru",
        "types[]": "city"
    }
    response2 = get(travelpayouts_url, params=params2).json()
    code2 = response2[0]["code"]
    with open("amadeus_keys.txt", 'r') as f:
        key, secret = f.read().split('\n')
    auth_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    auth_params = {
        "grant_type": "client_credentials",
        "client_id": key,
        "client_secret": secret
    }
    auth_headers = {
        "content-type": "application/x-www-form-urlencoded"
    }
    auth_response = post(auth_url, data=auth_params, headers=auth_headers).json()
    token = auth_response["access_token"]
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    params = {
        "originLocationCode": code1,
        "destinationLocationCode": code2,
        "departureDate": date,
        "adults": 1,
        "max": 10
    }
    headers = {
        "authorization": f"Bearer {token}"
    }
    response = get(url, params=params, headers=headers).json()
    text = "Информация о рейсах: \n\n"
    if not response["data"]:
        text += "К сожалению, рейсов в выбранный день нет."
    for offer in response["data"]:
        itineraries = offer["itineraries"][0]
        text += f"""Длительность полета: {itineraries["duration"][2:]
            .replace('H', ' ч ').replace('M', ' мин ')}
        Перелеты: \n"""
        for i, segment in enumerate(itineraries["segments"]):
            date1, time1 = segment["departure"]["at"].split('T')
            date2, time2 = segment["arrival"]["at"].split('T')
            c1 = segment["departure"]["iataCode"]
            c2 = segment["arrival"]["iataCode"]
            text += f"""        Участок {i + 1}: 
            Отправление {date1} в {time1}, {c1}
            Прибытие {date2} в {time2}, {c2} \n"""
        text += f"""Цена билета на 1 взрослого: {offer["price"]["total"]}{offer["price"]["currency"]}\n\n"""
    return text
