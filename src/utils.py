from typing import Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def create_retry_session(
    total_retries: int = 3,
    backoff_factor: float = 0.5,
    status_forcelist: Optional[tuple] = (429, 500, 502, 503, 504),
    timeout: float = 10.0,
) -> requests.Session:
    """
    Create a requests.Session with a Retry policy mounted.

    :param total_retries: total number of retries for idempotent requests
    :param backoff_factor: backoff multiplier
    :param status_forcelist: HTTP status codes to retry on
    :param timeout: default timeout (not applied inside session — use per-call)
    :return: configured Session
    """
    session = requests.Session()
    retries = Retry(
        total=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=frozenset(["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"])
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session
