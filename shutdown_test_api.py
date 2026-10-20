import pytest
import requests
from requests.exceptions import ConnectionError

BASE_URL = "http://localhost:4567"
project_id = None


def test_shutdown_server_connection_drop():
    # The Swagger spec dictates a 200 OK[cite: 1]
    # However, exploratory testing reveals the server abruptly drops the connection (Empty reply)
    try:
        requests.get(f"{BASE_URL}/shutdown")
        pytest.fail("Expected a connection drop based on exploratory testing, but request completed.")
    except ConnectionError as e:
        # Expected behavior: requests raises a ConnectionError when the server drops the connection
        error_msg = str(e)
        assert "Remote end closed connection without response" in error_msg or "Connection aborted" in error_msg or "Connection refused" in error_msg