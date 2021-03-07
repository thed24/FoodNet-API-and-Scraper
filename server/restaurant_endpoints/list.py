import inspect
import json
import os
import sys

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from entities.resteraunt import Restaurant


def get_restaurants(event, context):
    results_iter = Restaurant.scan()
    results = []
    [results.append(result) for result in results_iter]

    new_results = {}
    rest_duplicates = {}

    for result in results:
        if result.name in rest_duplicates:
            rest_duplicates[result.name].append(result)
        else:
            rest_duplicates[result.name] = [result]

    for result in results:
        average_rating = 0.0
        ratings = []
        open_hours = ""
        info = ""
        types = ""
        price_indicator = ""
        is_aggregated = False
        single_review_flag = False

        for rest in rest_duplicates[result.name]:
            if rest.service == "Google":
                open_hours = rest.open_hours
                info = rest.info
                price_indicator = rest.price_indicator

            if rest.service == "Zomato":
                types = rest.types

            if len(rest_duplicates[result.name]) == 2:
                is_aggregated = True

            ratings.append({"service": rest.service, "rating": rest.rating, "numberOfReviews": rest.review})

            try:
                if rest.rating is not None:
                    average_rating += float(rest.rating)
            except ValueError:
                single_review_flag = True
                average_rating += 0

        if is_aggregated:
            if "new_result" in new_results:
                new_result = new_results[rest.name]
            else:
                new_result = result.to_dict()

            new_result.pop("rating", None)
            new_result.pop("review", None)
            new_result.pop("service", None)

            if types is not "":
                new_result["types"] = types
            if open_hours is not "":
                new_result["open_hours"] = open_hours
            if info is not "":
                new_result["info"] = info
            if price_indicator is not "":
                new_result["price_indicator"] = price_indicator

            new_result["average_rating"] = average_rating if single_review_flag else average_rating / 2
            new_result["ratings"] = ratings

            print(new_result)
            new_results[rest.name] = new_result

    return {'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True
            },
            'body': json.dumps({'items': list(new_results.values())})}


if __name__ == '__main__':
    get_restaurants(None, None)
