from fetcher import FETCH_METHODS
import logging


def methods():
    methods = [
        {
            "name": name,
            "desc": meta["description"],
            "args": meta["arguments"]
        }
        for name, meta in FETCH_METHODS.items()
    ]

    response = {
        "body": {
            "methods": methods
        },
        "success": True,
    }
    return response
