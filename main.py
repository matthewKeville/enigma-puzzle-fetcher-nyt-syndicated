import warnings
import json
import fileinput
import requests
import logging
from requests.exceptions import JSONDecodeError
from requests.exceptions import HTTPError

from constants import VERSION, PLUGIN_NAME, DATE_MINIMUM, SCHEMA_BASE_URL
from exceptions import logAndRaise, UnimplementedError, FetcherParseError, UnsupportedFeatureError, ArgsError, FetchMethodError
from fetcher import fetch

# I threw my hands up at getting Resources and Registry to work..
# Suppress the specific deprecation warning related to jsonschema.RefResolver
warnings.filterwarnings(
    "ignore",
    message=r".*jsonschema.RefResolver is deprecated.*",
    category=DeprecationWarning
)

# linter keeps wanting this above warnings.filterwarning ...
from jsonschema.exceptions import ValidationError, SchemaError
from jsonschema import Draft7Validator, RefResolver

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("fetcher.log"),        # Log to file
    ],
)

schema_ids = [
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


def read_stdin_as_json():
    """
    Raises:
        JSONDecodeError:
    """
    try:
        lines = []
        for line in fileinput.input():
            lines.append(line)
        return json.loads("".join(lines))
    except json.decoder.JSONDecodeError as e:  # Name Conflict betweens request and json
        logAndRaise("Unable to decode input as JSON")


def read_stdin_as_json_spoof():
    """
    Raises:
        JSONDecodeError:
    """

    # invalid against schema
    # test_json_string = """
    #     {
    #         "body" : {
    #             "method" : "date",
    #             "args" : [ "04/04/2025" ]
    #         }
    #     }
    # """

    # valid against schema
    # test_json_string = """
    #     {
    #         "body" : {
    #             "method" : "date",
    #             "args" : [ "04/04/2025" ]
    #         },
    #         "requestType" : "fetch"
    #     }
    #   """

    # invalid method
    test_json_string = """
        {
            "body" : {
                "method" : "bullshit",
                "args" : [ "04/04/2025" ]
            },
            "requestType" : "fetch"
        }
      """

    # invalid bad requestType
    # test_json_string = """
    #     {
    #         "body" : {
    #             "method" : "date",
    #             "args" : [ "04/04/2025" ]
    #         },
    #         "requestType" : "bullshit"
    #     }
    #   """

    # not json
    # test_json_string = """asdkfjasdf"""

    # malformed json
    # test_json_string = """{asdf : "asdfasdf" }"""

    try:
        jsonData = json.loads(test_json_string)
    except json.JSONDecodeError as e:  # Name Conflict betweens request and json
        logAndRaise(e, "Unable to decode input as JSON")
    return jsonData


def get_schemas(schema_ids):
    """
    Raises:
        HTTPError:
        UnicodeDecodeError:
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
        except Exception as e:
            logAndRaise(e, f"Unknown error getting schema {id}")
    return schemas


def processRequest(request):
    match request["requestType"]:
        case "fetch":
            # TODO handdle fetch level errors and figure out flow for
            # ErrorResonse creation, we want the exception to flow up
            # here to insert it into the errorResponse
            try:
                return fetch(request["body"])
            except FetcherParseError as e:
                printErrorResponseAndExit("FetchFailed", e.message)
            except FetchMethodError as e:
                printErrorResponseAndExit("FetchFailed", e.message)
            except UnsupportedFeatureError as e:
                printErrorResponseAndExit("FetchFailed", e.message)
            except ArgsError as e:
                printErrorResponseAndExit("InvalidArgs", e.message)

        case "methods":
            logAndRaise(UnimplementedError, "methdos process unimplemented")
        case "args":
            logAndRaise(UnimplementedError, "args process unimplemented")


def printErrorResponseAndExit(code, errorMessage):
    logging.info("building error response")
    response = {
        "code": code,
        "errorMessage": errorMessage
    }
    print(response)
    exit(0)


try:
    schemas = get_schemas(schema_ids)
    resolver = RefResolver(
        SCHEMA_BASE_URL, schemas[schema_ids[0]], store=schemas)
    validator = Draft7Validator(
        schema=schemas["schemas/request-schema.json"], resolver=resolver)

    try:
        request = read_stdin_as_json_spoof()
        validator.validate(request)
        print(processRequest(request))
        exit(0)
    except json.decoder.JSONDecodeError as e:
        createErrorResponse("BadRequest",
                            f"Input is not valid JSON {e.msg}")
    except ValidationError as e:
        createErrorResponse("BadRequest",
                            f"Request doesn't not conform to schemas/request-body-schema.json {e.message}")

# if schemas are invalid
except SchemaError as e:
    logAndRaise(e, "Critical Error : Schema error")
    exit(1)

except Exception as e:
    logging.critical(
        f"Critical Error : Unanticipated {e.__class__.__name__} {e}")
    exit(1)
