# Regex Search Tool

## Overview
This tool recursively searches through files in a specified directory, applying regular expression patterns to identify potentially sensitive information, insecure code, or specific patterns defined by the user.

## Features
- Excludes specific file extensions, directories, and filenames from the search.
- Outputs findings to a designated output directory.
- Handles multiple programming languages with both general and language-specific regex patterns.

## Usage

### Command Line Arguments
- `directory`: Mandatory. The root directory to start the search.
- `-o, --output`: Optional. Specifies the output directory prefix to save results. Default is "output".
- `-e, --exclude_ext`: Optional. Specifies file extensions to exclude (comma-separated, include dot). Default is ".jpg, .png".
- `-f, --exclude_files`: Optional. Specifies file names to exclude (comma-separated). Default is "config.json, secrets.yml".
- `-d, --exclude_dirs`: Optional. Specifies directories to exclude (comma-separated, full path or relative to searched directory).

### Example Command
```
python regex-search-tool.py ./project -o results -e .jpg,.png -f config.json,secrets.yml -d ./temp,./backup
```

## Configuration
Modify the `excluded_extensions`, `excluded_dirs`, and `excluded_filenames` in the script to meet your specific requirements.

## Installation
No additional installation is required. Ensure Python is installed on your system.


