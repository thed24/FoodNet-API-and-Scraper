import requests
import json
import time
import os, sys, inspect

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from server.entities.resteraunt import Restaurant


class GooglePlaces(object):
    def __init__(self, api_key):
        super(GooglePlaces, self).__init__()
        self.apiKey = api_key

    def search_places_by_suburb(self, suburb, radius, types):
        endpoint_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        places = []
        params = {
            'location': suburb,
            'radius': radius,
            'types': types,
            'key': self.apiKey
        }
        res = requests.get(endpoint_url, params=params)
        results = json.loads(res.content)
        places.extend(results['results'])
        time.sleep(2)
        while "next_page_token" in results:
            params['pagetoken'] = results['next_page_token'],
            res = requests.get(endpoint_url, params=params)
            results = json.loads(res.content)
            places.extend(results['results'])
            time.sleep(2)
        return places

    def get_place_details(self, place_id, fields):
        endpoint_url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            'placeid': place_id,
            'fields': ",".join(fields),
            'key': self.apiKey
        }
        res = requests.get(endpoint_url, params=params)
        place_details = json.loads(res.content)
        return place_details


def check_for_filters(review_text):
    extra_filters = {
        "vegan": 0,
        "handicap_options": 0,
        "wifi": 0,
        "currently_open": False
    }

    if "wifi".upper() in map(str.upper, review_text):
        extra_filters["wifi"] += 1

    return json.dumps(extra_filters)


if __name__ == '__main__':
    api = GooglePlaces(os.environ["GOOGLE_PLACES_API_KEY"])
    places = api.search_places_by_suburb("37.8230 144.9980, Melbourne", "100", "restaurant")
    print("Places found: " + str(len(places)))
    fields = ['name', 'formatted_address', 'international_phone_number', 'rating', 'review']
    for place in places:
        details = api.get_place_details(place['place_id'], fields)

        if 'result' in details:
            rest_name = details['result']['name']
            rest_area = details['result']['formatted_address']
            print(rest_name)

            # Create DynamoDB entity or get existing entry
            try:
                current_restaurant = Restaurant.get(rest_name, rest_area)
            except Restaurant.DoesNotExist:
                current_restaurant = Restaurant(rest_name, rest_area)

            try:
                current_restaurant.phone = details['result']['international_phone_number']
            except KeyError:
                current_restaurant.phone = ""

            try:
                reviews = details['result']['reviews']
            except KeyError:
                reviews = []

            for review in reviews:
                text = str(review['text'])
                current_restaurant.info = check_for_filters(text)

            current_restaurant.service = "Google"
            current_restaurant.save()
