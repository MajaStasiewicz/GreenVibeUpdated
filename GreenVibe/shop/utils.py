from products.models import *

def generate_discount_code():
    discount_code = Code()
    discount_code.generate_unique_code()
    return discount_code