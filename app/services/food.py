import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)


def get_food_info(product_name: str) -> Optional[dict]:
    try:
        url = "https://world.openfoodfacts.org/cgi/search.pl"
        params = {
            "action": "process",
            "search_terms": product_name,
            "json": "true",
            "page_size": 1,
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            logger.warning("Food API error: %s", response.text)
            return None
        data = response.json()
        products = data.get("products", [])
        if not products:
            return None
        first = products[0]
        return {
            "name": first.get("product_name", product_name),
            "calories": first.get("nutriments", {}).get("energy-kcal_100g", 0),
        }
    except Exception as exc:
        logger.exception("Food exception: %s", exc)
        return None
