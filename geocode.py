from requests import get


def get_coordinates(address):
    with open("geocode_key.txt", 'r') as f:
        key = f.read()
    request = f"https://geocode-maps.yandex.ru/1.x/?apikey={key}&" \
              f"geocode={address}&format=json"
    response = get(request)
    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    return toponym["Point"]["pos"]

