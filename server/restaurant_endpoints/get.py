import inspect
import json
import os
import sys

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from entities.resteraunt import Restaurant


def get_restaurant(event, context):
    try:
        found_restaurant = Restaurant.get(hash_key=event['name']['area'])
    except Restaurant.DoesNotExist:
        return {'statusCode': 404,
                'body': json.dumps({'error_message': 'Restaurant was not found'})}

    # create a response
    return {'statusCode': 200,
            'body': json.dumps(dict(found_restaurant))}
