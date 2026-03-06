import json
import fileinput
import logging
from jsonschema.exceptions import ValidationError
from jsonschema import Draft7Validator
from exceptions import (
    logAndRaise,
    UnimplementedError,
    SchemaBuildError,
    FetchError,
    FetchMethodError,
    FetchArgsError,
    FetchParsingError,
    FetchUnsupportedError,
)
from info import info
from fetcher import fetch
from methods import methods
from schemas import REQUEST_SCHEMA,RESPONSE_SCHEMA
from constants import API_VERSION

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("log.log"),        # Log to file
    ],
)


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
        logAndRaise(e, "Unable to decode input as JSON")


def processRequest(request):
    match request["type"]:
        case "fetch":
            try:
                return fetch(request["fetch"])
            except FetchError as fe:
                return generateErrorResponse("fetchFailed", fe.message)
            exit(0)
        case "methods":
            return methods()
        case "info":
            return info()


def generateErrorResponse(code, errorMessage):
    logging.info("building error response")

    response = {
        "type": "error",
        "apiVersion": API_VERSION,
        "error": {
            "type": code,
            "errorMessage": errorMessage
        }
    }

    logging.info("error response built")
    logging.info(response)

    return response


response = None
try:
    validator = Draft7Validator(schema=REQUEST_SCHEMA)

    try:
        request = read_stdin_as_json()
        validator.validate(request)
        response = processRequest(request)
    except json.decoder.JSONDecodeError as e:
        response = generateErrorResponse(
            "BadRequest", f"Input is not valid JSON {e.msg}")
    except ValidationError as e:
        response = generateErrorResponse(
            "BadRequest", f"Request doesn't conform to schemas/request-body-schema.json {e.message}")

except SchemaBuildError as e:
    msg = f"SchemaError: {e.message}"
    logging.critical(msg)
    response = generateErrorResponse("CriticalFailure", msg)
except UnimplementedError as e:
    msg = f"UnimplementedError: {e.message}"
    logging.critical(msg)
    response = generateErrorResponse("CriticalFailure", msg)
except Exception as e:
    msg = f"Critical Error : Unanticipated {e.__class__.__name__} {e}"
    logging.critical(msg)
    response = generateErrorResponse("CriticalFailure", msg)

if response == None:
    msg = f"Critical Error : response is None"
    logging.critical(msg)
    response = generateErrorResponse("CriticalFailure", msg)

print(json.dumps(response))
exit(0)
