import inspect
import json
import os
import sys

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from entities.resteraunt import Restaurant


def get_restaurants(event, context):
    results = Restaurant.scan()
    result_dict = [dict(result.to_dict()) for result in results]

    return {'statusCode': 200,
            'body': json.dumps({'items': result_dict})}


if __name__ == '__main__':
    get_restaurants(None, None)