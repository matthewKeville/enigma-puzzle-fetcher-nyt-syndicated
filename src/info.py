import logging

def info():
    response = {
        "body": {
            "name": "nyt syndicated fetcher",
            "description": "fetches NYT syndicated puzzles through webscraping the SeattleTimes"
        },
        "success": True,
    }
    return response
