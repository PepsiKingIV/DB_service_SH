from dotenv import load_dotenv
import os

load_dotenv()

TINKOFF_TOKEN = os.environ.get("tinkoff_token")

DB_HOST = os.environ.get("DB_HOST")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")
DB_PORT = os.environ.get("DB_PORT")


DB_USER_TEST = os.environ.get("DB_USER_TEST")
DB_PASS_TEST = os.environ.get("DB_PASS_TEST")
DB_HOST_TEST = os.environ.get("DB_HOST_TEST")
DB_NAME_TEST = os.environ.get("DB_NAME_TEST")
DB_PORT_TEST = os.environ.get("DB_PORT_TEST")


SECRET_AUTH = os.environ.get("SECRET_AUTH")

SMTP_SERVER = os.environ.get("SMTP_SERVER")
EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")
