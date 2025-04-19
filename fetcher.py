import requests
import datetime
import json
from exceptions import UnsupportedFeatureError, FetcherParseError, UnimplementedError, ArgsError, FetchMethodError
from constants import DATE_MINIMUM, PLUGIN_NAME, VERSION

from exceptions import logAndRaise

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


def fetch(fetch_request_body):
    """
    Raises:
        FetcherParseError:
        FetchMethodError:
        UnsupportedFeatureError:
        ArgsError:
    """
    method = fetch_request_body["method"]
    match method:
        case "date":
            _fetch_by_date(*fetch_request_body["args"])
            pass
        case "today":
            logAndRaise(UnimplementedError,
                        " fetch method today is unimplemented")
        case _:
            logAndRaise(FetchMethodError,
                        f" fetch method {method} is unimplemented")


def _fetch_by_date(dateString):

    fmt = "%Y/%m/%d"
    try:
        date = datetime.datetime.strptime(dateString, fmt).date()
    except ValueError:
        logAndRaise(ArgsError, f"Unable to parse date format {dateString}")

    if date < DATE_MINIMUM:
        logAndRaise(
            ArgsError, f"date {date} exceeds minimum date {str(DATE_MINIMUM.date)}")
    if date > datetime.datetime.now().date():
        logAndRaise(ArgsError, f"date {date} exceeds current date")

    baseUrl = 'https://nytsyn.pzzl.com/nytsyn-crossword-mh/nytsyncrossword?date='
    url = baseUrl + date.strftime("%y%m%d")

    response = requests.get(url)
    response.raise_for_status()
    text = response.content.decode('utf-8', errors='ignore')

    installData = _parse_puzzle_file(text)
    return json.dumps(installData)


def _parse_puzzle_file(text):
    """
    Raises:
        FetcherParseError:
        UnsupportedFeatureError:
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
        logAndRaise(FetcherParseError,
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
            logAndRaise(UnsupportedFeatureError,
                        "Solution geometry contains \",\" characters")
        elif "." in line:
            logAndRaise(UnsupportedFeatureError,
                        "Solution geometry contains \".\" characters")
        elif "^" in line:
            logAndRaise(UnsupportedFeatureError,
                        "Solution geometry contains \"^\" characters")
        elif len(line) != columns:
            logAndRaise(UnsupportedFeatureError,
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
        logAndRaise(FetcherParseError,
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
        logAndRaise(FetcherParseError,
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
                    "Direction": "Across",
                    "Prompt": prompt,
                    "Answer": answer
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
                    "Direction": "Down",
                    "Prompt": prompt,
                    "Answer": answer
                })

    puzzleData = {
        "meta": {
            "plugin": PLUGIN_NAME,
            "pluginVersion": VERSION,
            "installedDate": str(datetime.datetime.now().date())
        },
        "columns": columns,
        "rows": rows,
        "clues": clues,
        "title": title,
        "author": author,
        "releaseDate": str(releaseDate.date())
    }

    return puzzleData
