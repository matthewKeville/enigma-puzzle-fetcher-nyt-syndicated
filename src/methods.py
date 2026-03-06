from fetcher import FETCH_METHODS
from constants import API_VERSION
import logging


def methods():
    methods = [
        {
            "name": name,
            "description": meta["description"],
            "arguments": meta["arguments"]
        }
        for name, meta in FETCH_METHODS.items()
    ]

    response = {
        "type": "methods",
        "apiVersion": API_VERSION,
        "methods": {
            "methods": methods
        }
    }
    return response
