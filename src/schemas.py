import requests
from requests.exceptions import JSONDecodeError
from requests.exceptions import HTTPError
from jsonschema.exceptions import SchemaError
from exceptions import logAndRaise
from constants import SCHEMA_BASE_URL

REQUEST_SCHEMA_URL = SCHEMA_BASE_URL + "/RequestSchema.json"
RESPONSE_SCHEMA_URL = SCHEMA_BASE_URL + "/ResponseSchema.json"

def _build_schema(schemaUrl):
    """
    Raises:
        HTTPError:
        UnicodeDecodeError:
        JSONDecodeError:
        SchemaError:
        Exception:
    """
    try:
        response = requests.get(schemaUrl)
        response.raise_for_status()
        schemaJson = response.json()
    except HTTPError as e:
        logAndRaise(e, f"Unable to get schema document{schemaUrl}")
    except UnicodeDecodeError as e:
        logAndRaise(e, f"Unable to decode content {schemaUrl}")
    except JSONDecodeError as e:
        logAndRaise(e, f"Unable to decode json {schemaUrl}")
    except SchemaError as e:
        logAndRaise(e, f"Schema is invalid {schemaUrl}")
    except Exception as e:
        logAndRaise(e, f"Unknown error getting schema {schemaUrl}")

    return schemaJson

REQUEST_SCHEMA = _build_schema(REQUEST_SCHEMA_URL)
RESPONSE_SCHEMA = _build_schema(RESPONSE_SCHEMA_URL)
