import logging


logger = logging.getLogger(__name__)



def generate_code(length=6):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

import random

def generate_public_id(model, field="public_id", start=100000, end=999999):
    while True:
        public_id = random.randint(start, end)
        if not model.objects.filter(**{field: public_id}).exists():
            return public_id


