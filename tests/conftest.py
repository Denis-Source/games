import re

import pytest
import requests
from neomodel import config as config_db, db

from config import get_neo4j_url, get_api_url

DEFAULT_TIMEOUT = 5


@pytest.fixture
def api(timeout=DEFAULT_TIMEOUT):
    requests.get(get_api_url(), timeout=DEFAULT_TIMEOUT)


@pytest.fixture
def neo4j(timeout=DEFAULT_TIMEOUT):
    config_db.DATABASE_URL = get_neo4j_url()
    cypher = "MATCH (n) RETURN distinct labels(n)"
    db.cypher_query(cypher)


def assert_url_is_http(url):
    assert re.match(r"^https?://", url)
