# Build Documentation

## Overview

The `build.sh` script creates an isolated instance of the project, 
including a `run.sh` script to launch the plugin from anywhere.

## Usage

To specify a custom build directory:

```sh
BUILD_DIR=<target-directory> ./build.sh
```

Otherwise, `./build` will be assumed
