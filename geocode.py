from requests import get


def get_coordinates(address):
    request = f"https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&" \
              f"geocode={address}&format=json"
    response = get(request)
    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    toponym_coordinates = toponym["Point"]["pos"]
    return toponym_coordinates

