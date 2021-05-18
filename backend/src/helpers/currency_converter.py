import re

import requests

from src.app import api


class CurrencyConversionError(Exception):
    """Raised when converting currency via convert endpoint"""

    pass


class CurrencySymbolsError(Exception):
    """Raised when fetching currency symbols from symbols endpoint"""

    pass


class CurrencyConverter:
    def __init__(
        self, url="", api_key=None, base_currency="", target_currency=""
    ) -> None:
        self._api_key = api_key
        self._url = url
        self._base_currency = base_currency
        self._target_currency = target_currency

    def fetch_currency_symbols(self):
        payload = {"access_key": self._api_key}
        response = requests.get(f"{self._url}/symbols", params=payload)

        if response.status_code == 200:
            return response.json()
        else:
            raise CurrencySymbolsError("Failure in retrieving symbols")

    def convert_currency(self):
        payload = {
            "access_key": self._api_key,
            "base": self._base_currency,
            "symbols": self._target_currency,
        }

        response = requests.get(f"{self._url}/latest", params=payload)

        if response.status_code == 200:
            return response.json()
        else:
            raise CurrencyConversionError("Error in converting currency value")
