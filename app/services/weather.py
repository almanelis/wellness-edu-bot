import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)


def get_temperature(city: str, api_key: Optional[str]) -> Optional[float]:
    if not api_key:
        return None
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "appid": api_key, "units": "metric"}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            logger.warning("Weather error: %s", response.text)
            return None
        data = response.json()
        return float(data["main"]["temp"])
    except Exception as exc:
        logger.exception("Weather exception: %s", exc)
        return None
