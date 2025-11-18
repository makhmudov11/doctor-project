import random
import logging
logger = logging.getLogger(__name__)



def generate_code(length=6):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])



