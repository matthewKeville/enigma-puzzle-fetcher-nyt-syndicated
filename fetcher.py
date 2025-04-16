import requests
import datetime
import json
import fileinput
from bs4 import BeautifulSoup

VERSION = "0.1"
PLUGIN_NAME = "SeattleTimesNYTPzzl"
DATE_MINIMUM = datetime.datetime(2016, 1, 1).date()

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


class UnsupportedFeatureError(Exception):
    pass


class ParseError(Exception):
    pass


def install_by_date(date: "datetime.date"):

    if date < DATE_MINIMUM:
        raise ValueError(f"date exceeds minimum date {str(DATE_MINIMUM.date)}")
    if date > datetime.datetime.now().date():
        raise ValueError(f"date exceeds current date")
    baseUrl = 'https://nytsyn.pzzl.com/nytsyn-crossword-mh/nytsyncrossword?date='
    url = baseUrl + date.strftime("%y%m%d")

    response = requests.get(url)
    response.raise_for_status()
    text = response.content.decode('utf-8', errors='ignore')

    installData = parse(text)
    return json.dumps(installData)


def parse(text):

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
        raise ParseError("format appears off, expected ARCHIVE as first line")

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
            raise UnsupportedFeatureError(
                "Solution geometry contains \",\" characters")
        elif "." in line:
            raise UnsupportedFeatureError(
                "Solution geometry contains \".\" characters")
        elif "^" in line:
            raise UnsupportedFeatureError(
                "Solution geometry contains \"^\" characters")
        elif len(line) != columns:
            raise UnsupportedFeatureError(
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
        raise ParseError(
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
        raise ParseError(
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

###############################################################################
# Plugin Command Schema


# install
"""
{
    "requestType" : "install",
    "installlRequest" : {
        "installType" : ( None , ... )
        "installArgs" : []
    }
}
"""

# spec
{
    "requestType": "spec"
}

# Plugin Response Schema

# install fail
"""
{
    "responseType" : "install"
    "success" : False
    "reason" : <String>
}
"""

# install success
"""
{
    "responseType" : "install"
    "success" : True
    "data" : {}
}
"""

# spec
"""
{
    "responseType" : "spec"
    "installCapabilities" : [
        {
            "name" : "date",
            "requiredArgs" : [ { "name" : "date" , "position" : 0 } ]
            "info" : "installs the puzzle released on the given date"
        }

    ]
}
"""
###############################################################################

lines = []
for line in fileinput.input():
    lines.append(line)
data = "".join(lines)

jsonData = json.loads(data)

if jsonData["requestType"] == "install":
    installData = jsonData["installRequest"]
    if installData["installType"] == "date":
        fmt = "%Y/%m/%d"
        date = datetime.datetime.strptime(
            jsonData["installRequest"]["installArgs"][0], fmt)
        #print(f"installing {str(date.date())}")
        jsonData = install_by_date(date.date())
        print(jsonData)


# fmt = "%Y/%m/%d"
# date = datetime.datetime.strptime(args.date, fmt)
# print(f"installing {str(date.date())}")
