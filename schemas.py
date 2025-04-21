import requests
from requests.exceptions import JSONDecodeError
from requests.exceptions import HTTPError
from jsonschema.exceptions import SchemaError
from referencing import Registry, Resource
from exceptions import logAndRaise
from constants import SCHEMA_BASE_URL

_schema_ids = [
    "schemas/puzzle-data-schema.json",
    "schemas/error-schema.json",

    "schemas/fetch/fetch-request-body-schema.json",
    "schemas/fetch/fetch-response-body-schema.json",

    "schemas/methods/method-schema.json",
    "schemas/methods/methods-response-body-schema.json",
    "schemas/methods/methods-request-body-schema.json",

    "schemas/request-schema.json",
    "schemas/response-schema.json"
]

def _build_schemas(schema_ids):
    schemas = {}
    """
    Raises:
        HTTPError:
        UnicodeDecodeError:
        JSONDecodeError:
        SchemaError:
        Exception:
    """
    for id in schema_ids:
        try:
            response = requests.get(f"{SCHEMA_BASE_URL}{id}")
            response.raise_for_status()
            schemaJson = response.json()
            schemas[id] = schemaJson
        except HTTPError as e:
            logAndRaise(e, f"Unable to get schema document{id}")
        except UnicodeDecodeError as e:
            logAndRaise(e, f"Unable to decode content {id}")
        except JSONDecodeError as e:
            logAndRaise(e, f"Unable to decode json {id}")
        except SchemaError as e:
            logAndRaise(e, f"Schema is invalid {id}")
        except Exception as e:
            logAndRaise(e, f"Unknown error getting schema {id}")

    return schemas


def _build_registry(schemas):
    pairs = []
    for id, schema in schemas.items():
        resource = Resource.from_contents(schema)
        pairs.append((id,resource))
    return Registry().with_resources(pairs)


SCHEMAS = _build_schemas(_schema_ids)
REGISTRY = _build_registry(SCHEMAS)
