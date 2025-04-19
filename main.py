import json
import fileinput
import logging
from jsonschema import Draft7Validator
from jsonschema.exceptions import ValidationError
from exceptions import (
    logAndRaise,
    UnimplementedError,
    FetcherParseError,
    UnsupportedFeatureError,
    ArgsError,
    FetchMethodError,
    SchemaBuildError
)
from fetcher import fetch


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
        logAndRaise(e,"Unable to decode input as JSON")


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
        "error" : {
            "code": code,
            "errorMessage": errorMessage
        },
        "success" : False,
    }
    print(json.dumps(response))
    exit(0)


try:
    from schemas import SCHEMAS, getRefResolver
except SchemaBuildError as e:
    printErrorResponseAndExit("CriticalFailure", f"{e}")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("fetcher.log"),        # Log to file
    ],
)

try:
    resolver = getRefResolver()
    validator = Draft7Validator(
        schema=SCHEMAS["schemas/request-schema.json"], resolver=resolver)

    try:
        request = read_stdin_as_json()
        validator.validate(request)
        print(processRequest(request))
        exit(0)
    except json.decoder.JSONDecodeError as e:
        printErrorResponseAndExit("BadRequest",
                                  f"Input is not valid JSON {e.msg}")
    except ValidationError as e:
        printErrorResponseAndExit("BadRequest",
                                  f"Request doesn't not conform to schemas/request-body-schema.json {e.message}")

# Unrecoverable, unanticipated error
except Exception as e:
    logging.critical(
        f"Critical Error : Unanticipated {e.__class__.__name__} {e}")
    exit(1)
