import os
import logging
import datetime

LOG_LEVEL = logging.INFO
logging.basicConfig(level=LOG_LEVEL)
DEBUG = True

API_VERSION = "v1.0"

HASH_ROUNDS = 3998
HASH_ALGO = "pbkdf2-sha512"
HASH_ALGO_CLS = "pbkdf2_sha512"
HASH_SALT_SIZE = 32

SECRET_KEY = os.getenv("SECRET_KEY")
SERVER_NAME = os.getenv("SERVER_NAME")

SESSION_COOKIE_NAME = "hack"
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_DOMAIN = ".{}".format(SERVER_NAME) if SERVER_NAME else None
SESSION_TYPE = 'mongodb'
PERMANENT_SESSION_LIFETIME = datetime.timedelta(hours=24)

REMEMBER_COOKIE_NAME = "well_hello_there"
REMEMBER_COOKIE_DURATION = datetime.timedelta(days=5)
REMEMBER_COOKIE_DOMAIN = ".{}".format(SERVER_NAME) if SERVER_NAME else None

INFLUX_HOST = "influx"
INFLUX_PORT = 8086
INFLUX_USER = "root"
INFLUX_PASSWORD = "root"
INFLUX_DATABASE = "hack"

LOGGER_NAME = "hack"

TEMPLATES = "{}/hack/views/templates".format(os.getcwd())

MONGO_HOST = "mongo"
MONGO_PORT = 27017
