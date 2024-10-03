import json
import requests
from geopy import distance
import folium
from flask import Flask
import codecs
from secret import map_key


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_min_distanse_coffe_shop(coffe_slovar):
    return coffe_slovar['distance']


def main():
    apikey = map_key
    place = input('Где вы находитесь? ')
    longitude_my, latitude_my = fetch_coordinates(apikey, place)
    my_place = latitude_my, longitude_my

    with open("coffee.json", "r", encoding="CP1251") as my_file:
        coffe_json = my_file.read()

    coffe = json.loads(coffe_json)
    coffe_slovar = []

    for coffeshop in coffe:
        coffe_title = coffeshop["Name"]
        coordinates_latitude = coffeshop["geoData"]["coordinates"][0]
        coordinates_longitude = coffeshop["geoData"]["coordinates"][1]
        distance_coffe = distance.distance(my_place, (coordinates_longitude, coordinates_latitude)).km
        coffe_slovar_cycle = {"title": coffe_title, "distance": f"{distance_coffe}", "latitude": coordinates_latitude,
                              "longitude": coordinates_longitude}
        coffe_slovar.append(coffe_slovar_cycle)

    slovar_for_map = sorted(coffe_slovar, key=get_min_distanse_coffe_shop)[:5]
    coffe_map = folium.Map(location=(my_place))

    for elem in slovar_for_map:
        folium.Marker(
            location=[elem.get("longitude"), elem.get('latitude')],
            tooltip="Показать",
            popup=elem.get('title'),
            icon=folium.Icon(icon="cloud"),
        ).add_to(coffe_map)

    coffe_map.save("coffe_map.html")

    app = Flask(__name__)

    @app.route('/')
    def hello():
        with codecs.open('coffe_map.html', 'r', "utf_8_sig") as f:
            content = f.read()
            return content

    app.run()


if __name__ == '__main__':
    main()
