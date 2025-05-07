import requests
import datetime
import json
import logging
from exceptions import (
    UnimplementedError,
    FetchError,
    FetchArgsError,
    FetchMethodError,
    FetchNetworkError,
    FetchParsingError,
    FetchUnsupportedError,
)
from constants import DATE_MINIMUM, PLUGIN_NAME, VERSION

from exceptions import logAndRaise

DATE_FMT = "%Y/%m/%d"

# request types [ Date ]
# request type restrictions
# Date : xx/xx/xx - yy/yy/yy

#  Strange Puzzles
#
# 'https://nytsyn.pzzl.com/nytsyn-crossword-mh/nytsyncrossword?date=250409'
#  Has a vertical column of '.' on the right side the solution geometry
#
#  https://nytsyn.pzzl.com/nytsyn-crossword-mh/nytsyncrossword?date=250209
#  Includes ',' in the character set for solution geometry, this extneds
#  the row line past the determined column number.
#  In other puzzles , seems to denote an optional but in this one
#  there are multiple and the answer i'm looking up don't appear to make optionals
#  like 'HAIREXT,E,N' for "They might be sewn in at a beauty parlor
#  like 'BUYGETONEFREE' for "Common Sales Promotion"
#
#  https://nytsyn.pzzl.com/nytsyn-crossword-mh/nytsyncrossword?date=250109
#  Inclues '^' in character set for solution geometry, this extends row line
#  past the determined column number
#  *I guess it's rebuses?*
#
#  https://nytsyn.pzzl.com/nytsyn-crossword-mh/nytsyncrossword?date=250309
#  includes ',' in solution geometry character set
#  in this puzzle this most definitely means optionals
#  "J,POKER" for "Card/game"

#  Known Well Behaved
#  https://nytsyn.pzzl.com/nytsyn-crossword-mh/nytsyncrossword?date=250404

# construct a decorator to inspect the available fetch methods elsewhere
FETCH_METHODS = {}


def fetch_method(name: str, description: str, arguments: dict):
    def decorator(func):
        FETCH_METHODS[name] = {
            "description": description,
            "arguments": arguments,
        }
        return func
    return decorator


def fetch(fetch_request_body):
    """
    Args:
        fetch-request-body (dictionary) : Compliant to scheams/fetch-request-body-schema.json
    Returns:
        fetch-response-body-schema (dictionary)  : Compliant to schemas/fetch-response-body-schema.json
    Raises:
        UnimplementedError,
        FetchError,
        FetchMethodError,
        FetchArgsError,
        FetchParsingError,
        FetchUnsupportedError,
    """
    logging.debug("in fetch")  # REMOVE ME
    method = fetch_request_body["method"]
    puzzle_data = None
    match method:
        case "date":
            puzzle_data = _fetch_by_date(*fetch_request_body["args"])
        case "today":
            puzzle_data = _fetch_by_today(*fetch_request_body["args"])
        case _:
            logAndRaise(FetchMethodError,
                        f" fetch method {method} is invalid")

    response = {
        "body": {
            "puzzleData": puzzle_data
        },
        "responseType": "fetch",
        "success": True,
    }
    return response


@fetch_method(
    name="date",
    description="Fetches the NYT Syndicated crossword for a given date.",
    arguments=[
        {
            "name": "date",
            "desc": "the date release of the puzzle",
            "constraints": [
                f"date must be in format {DATE_FMT}",
                f"date must be after {DATE_MINIMUM}",
                f"date must be before {str(datetime.datetime.now().date() + datetime.timedelta(days=1))}"
            ]
        }
    ]
)
def _fetch_by_date(dateString):
    """
    Args:
        dateString (string) : the target crossword release date "%Y/%m/%d"
    Returns:
        puzzle-data (dictionary)  : Compliant to schemas/puzzle-data-schema.json
    Raises:
        FetchArgsError,
        FetchNetworkError,
        FetchParsingError,
        FetchUnsupportedError,
    """

    try:
        date = datetime.datetime.strptime(dateString, DATE_FMT).date()
    except ValueError:
        logAndRaise(FetchArgsError,
                    f"Unable to parse date format {dateString}")

    if date < DATE_MINIMUM:
        logAndRaise(
            FetchArgsError, f"date {date} exceeds minimum date {str(DATE_MINIMUM.date)}")
    if date > datetime.datetime.now().date():
        logAndRaise(FetchArgsError, f"date {date} exceeds current date")

    text = _get_puzzle_by_date(date)
    installData = _parse_puzzle_file(text)
    return json.dumps(installData)


@fetch_method(
    name="today",
    description="Fetches the NYT Syndicated crossword for today.",
    arguments=[]
)
def _fetch_by_today():
    """
    Returns:
        puzzle-data (dictionary)  : Compliant to schemas/puzzle-data-schema.json
    Raises:
        FetchNetworkError,
    """
    text = _get_puzzle_by_date(datetime.date.today())
    installData = _parse_puzzle_file(text)
    return json.dumps(installData)


def _get_puzzle_by_date(date):
    """
    Args:
        text (string) : text from file retrieved from nytsyn.pzzl.com endpoint
    Returns:
        puzzle-data (dictionary)  : Compliant to schemas/puzzle-data-schema.json
    Raises:
        FetchNetworkError:
    """
    try:
        baseUrl = 'https://nytsyn.pzzl.com/nytsyn-crossword-mh/nytsyncrossword?date='
        url = baseUrl + date.strftime("%y%m%d")
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.Timeout as e:
        logAndRaise(FetchNetworkError, f"Timeout trying to GET {url} : {str(e)} ")
    except requests.exceptions.RequestException as e:
        logAndRaise(FetchNetworkError, f"Failed to GET {url} : {str(e)}")
    return response.content.decode('utf-8', errors='ignore')


def _parse_puzzle_file(text):
    """
    Args:
        text (string) : text from file retrieved from nytsyn.pzzl.com endpoint
    Returns:
        puzzle-data (dictionary)  : Compliant to schemas/puzzle-data-schema.json
    Raises:
        FetchParsingError:
        FetchUnsupportedError:
    """

    lines = text.split('\n')

    # 0 is ARCHIVE
    # 2 is YYMMDD
    # 4 is Puzzle Name
    # 6 is Author(s)
    # 8 is puzzle width
    # 10 is puzzle height
    # 16 is start of puzzle geometry : lineHeight = G
    # 16+G+1 is Across clues : acrossCluesCount = C
    # (16+G+1) + C + 1 is Down Clues : DownCluesCount = D

    ###################################
    # Integrity Check "ARCHIVE" Line
    ###################################
    if lines[0] != "ARCHIVE":
        logAndRaise(FetchParsingError,
                    "format appears off, expected ARCHIVE as first line")

    ###################################
    # Puzzle Data
    ###################################

    releaseDate = lines[2]  # yymmdd -> yyyymmdd
    releaseDate = "20"+releaseDate
    releaseDate = datetime.datetime.strptime(releaseDate, '%Y%m%d')

    title = lines[4]
    author = lines[6]
    rows = int(lines[8])
    columns = int(lines[10])
    acrossClueCount = int(lines[12])
    downClueCount = int(lines[14])

    ###################################
    # Extract Solution Geometry
    ###################################

    solution = [['*'] * (columns+1) for i in range(0, rows+1)]
    ln = 16
    while (lines[ln] != ""):
        line = lines[ln]
        if "," in line:
            logAndRaise(FetchUnsupportedError,
                        "Solution geometry contains \",\" characters")
        elif "." in line:
            logAndRaise(FetchUnsupportedError,
                        "Solution geometry contains \".\" characters")
        elif "^" in line:
            logAndRaise(FetchUnsupportedError,
                        "Solution geometry contains \"^\" characters")
        elif len(line) != columns:
            logAndRaise(FetchUnsupportedError,
                        f"Solution geometry contradicts row length : line length {len(line)} columns {columns}")

        for i, c in enumerate(line):
            solution[ln-16][i] = c
        ln += 1

    ###################################
    # Extract Across Clues
    ###################################
    acrossClues = []
    ln += 1
    acrossStop = ln + acrossClueCount
    while (ln != acrossStop):
        acrossClues.append(lines[ln])
        ln += 1
    # Integrity Check AC matches actual
    if len(acrossClues) != acrossClueCount:
        logAndRaise(FetchParsingError,
                    f"Across Clues Count Integrity Check Failed : expected {acrossClueCount} got {len(acrossClues)}")

    ###################################
    # Extract Down Clues
    ###################################
    downClues = []
    ln += 1
    downStop = ln + downClueCount
    while (ln != downStop):
        downClues.append(lines[ln])
        ln += 1
    # Integrity Check DC matches actual
    if len(downClues) != downClueCount:
        logAndRaise(FetchParsingError,
                    f"Down Clues Count Integrity Check Failed : expected {downClueCount} got {len(downClues)}")

    ###################################
    # Reconstitute into standard format
    ###################################

    clues = []

    for j in range(0, rows):
        for i in range(0, columns):

            # not a word start
            if solution[j][i] == '#':
                continue

            # encountered start of across clue
            if i != (columns-1) and (i == 0 or solution[j][i-1] == '#'):
                # parse answer
                answer = ""
                x = i
                while x != (columns) and solution[j][x] != '#':
                    answer += solution[j][x]
                    x += 1
                # reconsitute
                prompt = acrossClues.pop(0)
                clues.append({
                    "x": i,
                    "y": j,
                    "i": acrossClueCount - len(acrossClues),
                    "direction": "Across",
                    "prompt": prompt,
                    "answer": answer
                })

            # encountered start of down clue
            if j != (rows-1) and (j == 0 or solution[j-1][i] == '#'):
                # parse answer
                answer = ""
                y = j
                while y != (rows) and solution[y][i] != '#':
                    answer += solution[y][i]
                    y += 1
                prompt = downClues.pop(0)
                clues.append({
                    "x": i,
                    "y": j,
                    "i": downClueCount - len(downClues),
                    "direction": "Down",
                    "prompt": prompt,
                    "answer": answer
                })

    puzzleData = {
        "meta": {
            "plugin": PLUGIN_NAME,
            "pluginVersion": VERSION,
            "fetchDate": str(datetime.datetime.now().date())
        },
        "columns": columns,
        "rows": rows,
        "clues": clues,
        "title": title,
        "author": author,
        "releaseDate": str(releaseDate.date())
    }

    return puzzleData
