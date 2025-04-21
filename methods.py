from fetcher import FETCH_METHODS
import logging


def methods(methods_request_body):
    """
    Args:
    Returns:
    Raises:
    """
    logging.debug("ATK in methods 1") # ATK DELETE ME

    # if not methods_request_body["fetchAll"]:
    # else:

    methods = [
        {
            "name": name,
            "desc": meta["description"],
            "args": meta["arguments"]
        }
        for name, meta in FETCH_METHODS.items()
    ]

    logging.debug("ATK in methods 2") # ATK DELETE ME

    response = {
        "body": {
            "methods": methods
        },
        "success": True,
    }
    return response
