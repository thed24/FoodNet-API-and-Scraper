import json

from domain.entities.resteraunt import Restaurant


def get_restaurants():
    results = Restaurant.scan()

    return {'statusCode': 200,
            'body': json.dumps({'items': [dict(result) for result in results]})}
