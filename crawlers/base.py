import random
import time
import logging
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry



class BaseCrawler:
    USER_AGENT = (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/137.0 Safari/537.36"
    )

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.session = Session()

        retry = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[
                429,
                500,
                502,
                503,
                504,
            ],
            allowed_methods=["GET"],
        )

        adapter = HTTPAdapter(max_retries=retry)

        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self.session.headers.update({
            "User-Agent": self.USER_AGENT,
        })

    def sleep(self):
        time.sleep(random.uniform(0.4, 0.8))

    def get(self, url, **kwargs):
        response = self.session.get(
            url,
            timeout=20,
            **kwargs,
        )

        response.raise_for_status()

        self.sleep()

        return response