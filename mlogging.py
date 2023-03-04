import logging
logging.basicConfig(level=logging.DEBUG)
logging.debug('So should this')

def log(text):
    logging.debug(text)