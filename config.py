import os

LOADING_FOLDER = r"C:\Shlack\python\games\loading\apps"
DEFAULT_DB_USERNAME = "neo4j"


def get_neo4j_url(username=DEFAULT_DB_USERNAME):
    host = os.environ.get("DB_HOST", "localhost")
    port = 7687
    password = os.environ.get("DB_PASSWORD", "password")
    return f"bolt://{username}:{password}@{host}:{port}/"


def get_api_url():
    host = os.environ.get("API_HOST", "localhost")
    port = 5000
    return f"http://{host}:{port}"
