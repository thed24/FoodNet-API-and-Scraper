import json

from domain.entities.resteraunt import Restaurant


def get_restaurant(event, context):
    try:
        found_restaurant = Restaurant.get(hash_key=event['name']['area'])
    except Restaurant.DoesNotExist:
        return {'statusCode': 404,
                'body': json.dumps({'error_message': 'Restaurant was not found'})}

    # create a response
    return {'statusCode': 200,
            'body': json.dumps(dict(found_restaurant))}
