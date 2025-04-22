# enigma-puzzle-fetcher-nyt-syndicated

This project is a plugin for the [Enigma crossword application](https://github.com/matthewKeville/enigma), specifically designed to 
fetch syndicated puzzles from The New York Times (NYT). The plugin adheres to the 
JSON schema for Enigma's puzzle-fetching system and allows easy integration into 
the larger puzzle-fetching ecosystem.

## Features

- Fetches NYT syndicated crossword puzzles
- Supports JSON schema integration for easy parsing and usage
- Compatible with the Enigma Puzzle Fetcher system
- Provides an easy way to include NYT puzzles into crossword apps or websites

## Installation

1. Clone the repository:
2. Navigate to the project directory:
3. Execute the build script `build.sh` see [./docs/BUILD.md](BUILD.md)

  ### Development

  [build.sh](build.sh) will build a deployed version of the software, for
  local development, you should fulfill the dependencies in the project directory
  inside a virtual environment.

  ```sh
    python3 -m venv venv
    pip install -r requirements.txt
    source venv/bin/activate
  ```


## Usage

This plugin is intended to be used as part of the Enigma crossword application.
It processes requests through STDIN conformant to [enigma-puzzle-fetcher-schema](https://github.com/matthewKeville/enigma-puzzle-fetcher-schema)
and generates responses to STDOUT.

This project can be used as a standalone tool, to fetch NYT Syndicated crosswords,
so long as you provide a proper JSON request.

> Example usages

```sh
  # discover methods
  ./run.sh <<EOF
  {
      "body" : {
          "requestAll" : true,
      },
      "requestType" : "methods"
  }
  EOF
```

```sh
  # fetch "date" method
  ./run.sh <<EOF
  {
      "body" : {
          "method" : "date",
          "args" : [ "2024/04/20" ]
      },
      "requestType" : "fetch"
  }
  EOF
```

> Example usage
```sh
  # fetch "today" method
  ./run.sh <<EOF
  {
      "body" : {
          "method" : "today",
          "args" : []
      },
      "requestType" : "fetch"
  }
  EOF
```
