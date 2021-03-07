import os

from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute


class Restaurant(Model):
    class Meta:
        table_name = "aggregate-data"
        if "IN_LAMBDA" not in os.environ:
            aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
            aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
        region = 'ap-southeast-2'

    def to_dict(self):
        rval = {}
        for key in self.attribute_values:
            rval[key] = self.__getattribute__(key)
        return rval

    name = UnicodeAttribute(hash_key=True)
    area = UnicodeAttribute(range_key=True)
    types = UnicodeAttribute(null=True)
    rating = UnicodeAttribute(null=True)
    review = UnicodeAttribute(null=True)
    price_for_two = UnicodeAttribute(null=True)
    address = UnicodeAttribute(null=True)
    phone = UnicodeAttribute(null=True)
    info = UnicodeAttribute(null=True)
    additional_info = UnicodeAttribute(null=True)
    service = UnicodeAttribute(null=True)
