import logging
from constants import VERSION,API_VERSION

def info():
    response = {
        "type": "info",
        "apiVersion": API_VERSION,
        "fetch": {
            "name": "nyt syndicated fetcher",
            "description": "fetches NYT syndicated puzzles through webscraping the SeattleTimes",
            "version": VERSION
        },
    }
    return response
