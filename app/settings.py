import logging

logging.basicConfig(level=logging.DEBUG)

COOKIE_PARAMS = {
    'cookie_name': "file_upload",
    'identifier': "general_verifier",
    'secret_key': "DONOTUSE",
    'max_age': 3600
}

REDIS_PARAMS = {
    'host': "db",
    'port': 6379,
    'user': "user",
    'password': "CzsqvJwjY3U5!9SD"
}
