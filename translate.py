from requests import request


def en_ru(text):
    url = "https://translated-mymemory---translation-memory.p.rapidapi.com/api/get"
    querystring = {"langpair": "en|ru", "q": text, "mt": "1", "onlyprivate": "0", "de": "a@b.c"}
    headers = {
        "X-RapidAPI-Host": "translated-mymemory---translation-memory.p.rapidapi.com",
        "X-RapidAPI-Key": "709cfc75cemsh7ded4e8eef027dcp19c59djsn4105e8235097"
    }
    response = request("GET", url, headers=headers, params=querystring)
    return response.json()["responseData"]["translatedText"]
