import warnings
import requests
from requests.exceptions import JSONDecodeError
from requests.exceptions import HTTPError
from jsonschema.exceptions import SchemaError
# linter keeps wanting this above warnings.filterwarning ...
from constants import VERSION, PLUGIN_NAME, SCHEMA_BASE_URL
from exceptions import logAndRaise

# I threw my hands up at getting Resources and Registry to work..
# Suppress the specific deprecation warning related to jsonschema.RefResolver
warnings.filterwarnings(
    "ignore",
    message=r".*jsonschema.RefResolver is deprecated.*",
    category=DeprecationWarning
)

from jsonschema import RefResolver

_schema_ids = [
    "schemas/puzzle-data-schema.json",
    "schemas/error-schema.json",
    "schemas/args/args-response-body-schema.json",
    "schemas/args/args-request-body-schema.json",
    "schemas/fetch/fetch-request-body-schema.json",
    "schemas/fetch/fetch-response-body-schema.json",
    "schemas/methods/methods-response-body-schema.json",
    "schemas/request-schema.json",
    "schemas/response-schema.json"
]

_schemas = None

def _get_schemas(schema_ids):
    """
    Raises:
        HTTPError:
        UnicodeDecodeError:
        JSONDecodeError:
        SchemaError:
        Exception:
    """
    schemas = {}
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

# I wanted to construct the resolver once and bundle it into _get_schemas_and_resolver
# and expose RESOLVER, but for some reason running the validator twice with this
# resolver introduced errors I don't comprehend.
def getRefResolver():
    return RefResolver(
        SCHEMA_BASE_URL, SCHEMAS[_schema_ids[0]], store=SCHEMAS)

if _schemas is None:
    _schemas = _get_schemas(_schema_ids)

SCHEMAS = _schemas


