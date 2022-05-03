from requests import request


def en_ru(text):
    url = "https://translated-mymemory---translation-memory.p.rapidapi.com/api/get"
    querystring = {"langpair": "en|ru", "q": text,
                   "mt": "1", "onlyprivate": "0", "de": "a@b.c"}
    with open("translate_key.txt", 'r') as f:
        key = f.read()
    headers = {
        "X-RapidAPI-Host": "translated-mymemory---translation-memory.p.rapidapi.com",
        "X-RapidAPI-Key": key
    }
    response = request("GET", url, headers=headers, params=querystring)
    return response.json()["responseData"]["translatedText"]
