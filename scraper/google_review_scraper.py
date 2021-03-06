import requests
import json
import time
import os, sys, inspect
from suburbs import getMelbourneSuburbs
from geopy.geocoders import Nominatim


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


def check_for_filters(review_text, filter_dict):
    if "wifi".upper() in map(str.upper, review_text):
        filter_dict["wifi"] += 1
    if "vegan".upper() in map(str.upper, review_text):
        filter_dict["vegan"] += 1
    if "wheelchair".upper() in map(str.upper, review_text):
        filter_dict["wheelchair"] += 1
    if "train".upper() in map(str.upper, review_text):
        filter_dict["train"] += 1
    return filter_dict


def scrape_google(event, context):
    for suburb in getMelbourneSuburbs():
        gn = Nominatim(user_agent="thed24")
        suburb_long_lat = gn.geocode(suburb)
        api = GooglePlaces(os.environ["GOOGLE_PLACES_API_KEY"])
        places = api.search_places_by_suburb(
            str(suburb_long_lat.latitude) + "," + str(suburb_long_lat.longitude), "100", "restaurant"
        )
        print("Places found: " + str(len(places)))
        fields = ['name', 'formatted_address', 'international_phone_number',
                    'rating', 'review', "opening_hours", "price_level"]

        for place in places:
            details = api.get_place_details(place['place_id'], fields)
            extra_filters = {
                "vegan": 0,
                "handicap_options": 0,
                "wifi": 0,
                "currently_open": "",
                "near_train": 0,
            }

            if 'result' in details:
                rest_name = details['result']['name']
                print(rest_name)

                # Create DynamoDB entity or get existing entry
                try:
                    current_restaurant = Restaurant.get(rest_name, "Google")
                except Restaurant.DoesNotExist:
                    current_restaurant = Restaurant(rest_name, "Google")

                try:
                    current_restaurant.address = details['result']['formatted_address']
                except KeyError:
                    current_restaurant.address = ""

                try:
                    current_restaurant.rating = str(details['result']['rating'])
                except KeyError:
                    current_restaurant.rating = ""

                try:
                    current_restaurant.phone = details['result']['international_phone_number']
                except KeyError:
                    current_restaurant.phone = ""

                try:
                    reviews = details['result']['reviews']
                except KeyError:
                    reviews = []

                current_restaurant.review = str(len(reviews)) + " Reviews"
                for review in reviews:
                    text = str(review['text'])
                    extra_filters = check_for_filters(text, extra_filters)

                try:
                    price_level = details['result']['price_level']
                    current_restaurant.price_indicator = str(price_level)
                except KeyError:
                    None

                try:
                    extra_filters["currently_open"] = details['result']['opening_hours']['open_now']
                except KeyError:
                    None

                try:
                    opening_hours = details['result']['opening_hours']['periods']
                    current_restaurant.open_hours = str(opening_hours)
                except KeyError:
                    None

                current_restaurant.info = json.dumps(extra_filters)

                for x in range(0, 4):
                    try:
                        current_restaurant.save()
                        str_error = None
                    except Exception as error:
                        str_error = str(error)

                    if str_error:
                        time.sleep(2)
                    else:
                        break

if __name__ == '__main__':
    scrape_google()
