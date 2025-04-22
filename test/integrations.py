import subprocess
import json
from jsonschema import Draft7Validator
from schemas import SCHEMAS, getRefResolver

def _run_with_input(input_data):
    result = subprocess.run(
        ["python", "main.py"],
        input=input_data,
        capture_output=True,
        text=True
    )
    return (result.stdout, result.stderr)


def _validate(schemaId, json_data):
    validator = Draft7Validator(
        schema=SCHEMAS[schemaId], resolver=getRefResolver())
    validator.validate(json_data)

################################################################################
# Bad JSON
################################################################################

def test_not_json(capsys):
    """ Doesn't throw ValidationError """
    """ Doesn't throw json.decoder.JSONDecodeError """
    """ STDOUT returns response-schema w/ success is false """
    stdin = """asdkfjasdf"""
    stdout, stderr = _run_with_input(stdin)
    json_out = json.loads(stdout.strip())
    print(json_out)
    _validate("schemas/response-schema.json", json_out)
    assert(json_out["success"] == False)


def test_malformed_json(capsys):
    """ Doesn't throw ValidationError """
    """ Doesn't throw json.decoder.JSONDecodeError """
    """ STDOUT returns response-schema w/ success is false """
    stdin = """{asdf : "asdfasdf" }"""
    stdout, stderr = _run_with_input(stdin)
    json_out = json.loads(stdout.strip())
    print(f"json out is \n {json_out}")
    _validate("schemas/response-schema.json", json_out)
    assert(json_out["success"] == False)

################################################################################
# Nonconformant
################################################################################

def test_bad_requestType(capsys):
    """ Doesn't throw ValidationError """
    """ Doesn't throw json.decoder.JSONDecodeError """
    """ STDOUT returns response-schema w/ success is false """
    stdin = """
        {
            "body" : {
                "method" : "date",
                "args" : [ "04/04/2025" ]
            },
            "requestType" : "bullshit"
        }
      """
    stdout, stderr = _run_with_input(stdin)
    json_out = json.loads(stdout.strip())
    print(f"json out is \n {json_out}")
    _validate("schemas/response-schema.json", json_out)
    assert(json_out["success"] == False)


################################################################################
# Conformant, Invalid Data
################################################################################

def test_bad_fetch_method(capsys):
    """ Doesn't throw ValidationError """
    """ Doesn't throw json.decoder.JSONDecodeError """
    """ STDOUT returns response-schema w/ success is false """

    stdin = """
        {
            "body" : {
                "method" : "bullshit",
                "args" : [ "04/04/2025" ]
            },
            "requestType" : "fetch"
        }
    """
    stdout, stderr = _run_with_input(stdin)
    print(f"stdout is \n {stdout}")
    json_out = json.loads(stdout.strip())
    print(f"json out is \n {json_out}")
    _validate("schemas/response-schema.json", json_out)
    assert(json_out["success"] == False)


# Conformant

# valid_fetch = """
#     {
#         "body" : {
#             "method" : "date",
#             "args" : [ "04/04/2025" ]
#         },
#         "requestType" : "fetch"
#     }
#   """
