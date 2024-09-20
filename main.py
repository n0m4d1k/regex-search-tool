import os
import re
import sys
import argparse

# Define the file type mapping
file_type_map = {
    '.py': 'python',
    '.sh': 'bash',
    '.c': 'c',
    '.cpp': 'cpp',
    '.js': 'javascript',
    '.html': 'html',
    '.java': 'java',
    '.pl': 'perl',
    '.pm': 'perl',
    '.ts': 'typescript'
}

def load_regex_patterns(directory):
    """
    Load regex patterns from individual .txt files in a specified directory,
    ignoring any files in a 'disabled' subdirectory.

    Args:
        directory (str): Directory containing regex .txt files.

    Returns:
        dict: Dictionary of regex patterns with the filename as the key.
    """
    regex_patterns = {}
    for root, _, files in os.walk(directory):
        # Skip the 'disabled' directory
        if 'disabled' in root.split(os.sep):
            continue
        
        for filename in files:
            if filename.endswith('.txt'):
                pattern_name = filename[:-4]  # Remove the .txt extension to use as the pattern name
                with open(os.path.join(root, filename), 'r') as file:
                    pattern = file.read().strip()
                    regex_patterns[pattern_name] = pattern
    return regex_patterns

def get_file_type(file_path):
    _, ext = os.path.splitext(file_path)
    return file_type_map.get(ext)

def strip_bad_chars(text):
    """
    Strip bad characters from the text.

    Args:
        text (str): The text to be stripped.

    Returns:
        str: The cleaned text.
    """
    # Define characters to strip, e.g., non-alphanumeric except spaces and basic punctuation
    return re.sub(r'[^a-zA-Z0-9\s.,;:!?\'\"(){}[\]@#&*-_+=]', '', text)

def search_file(file_path, excluded_extensions, excluded_dirs, excluded_filenames, output_directory, strip_chars=False):
    if should_skip_file(file_path, excluded_extensions, excluded_dirs, excluded_filenames):
        return

    _, ext = os.path.splitext(file_path)
    language = file_type_map.get(ext)

    # Apply the regex patterns for general searches and language-specific searches
    applicable_regexes = general_regexes.copy()  # Start with general regexes

    if language and language in language_specific_regexes:
        applicable_regexes.update(language_specific_regexes[language])  # Add language-specific regexes

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                for regex_name, regex in applicable_regexes.items():
                    try:
                        matches = re.finditer(regex, line)  # Use finditer to capture full match objects
                        for match in matches:
                            full_match = match.group()  # Get the full match
                            
                            # Optionally strip unwanted characters from the match
                            if strip_chars:
                                full_match = strip_bad_chars(full_match)

                            # Capture the full line where the match was found
                            full_line = line.strip()

                            # Optionally strip unwanted characters from the line
                            if strip_chars:
                                full_line = strip_bad_chars(full_line)

                            # Capture the context around the match
                            start_line = max(i - 10, 0)
                            end_line = min(i + 11, len(lines))
                            context_lines = lines[start_line:end_line]
                            context = ''.join(context_lines).strip()

                            # Optionally strip unwanted characters from context
                            if strip_chars:
                                context = strip_bad_chars(context)

                            # Format the keywords properly without breaking
                            matched_keywords = ', '.join([str(m.group()) for m in re.finditer(regex, line)])
                            
                            result = (f"Match found in {file_path} at line {i + 1} for pattern {regex_name}. \n"
                                      f"Keywords: {matched_keywords}\nMatching String: {full_line}\n\n{context}\n\n")
                            output_filename = os.path.join(output_directory, f"{regex_name}_matches.txt")
                            os.makedirs(os.path.dirname(output_filename), exist_ok=True)
                            with open(output_filename, "a", encoding='utf-8') as output_file:
                                output_file.write(result)
                    except re.error as regex_error:
                        error_message = f"Error with regex '{regex_name}' in {file_path}: {str(regex_error)}"
                        error_filename = os.path.join(output_directory, f"{regex_name}_errors.txt")
                        os.makedirs(os.path.dirname(error_filename), exist_ok=True)
                        with open(error_filename, "a", encoding='utf-8') as error_file:
                            error_file.write(error_message + "\n")
    except IOError as io_error:
        error_message = f"Error reading {file_path}: {str(io_error)}"
        print(error_message)
        log_filename = os.path.join(output_directory, "file_read_errors.txt")
        os.makedirs(os.path.dirname(log_filename), exist_ok=True)
        with open(log_filename, "a", encoding='utf-8') as log_file:
            log_file.write(error_message + "\n")

def should_skip_file(file_path, excluded_extensions, excluded_dirs, excluded_filenames):
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()  # Ensuring case-insensitive comparison

    # Check if the file extension is in the excluded list
    if any(ext == excluded_ext.lower() for excluded_ext in excluded_extensions):
        return True

    # Check if the file's directory is in the excluded list
    if any(excluded_dir.lower() in file_path.lower() for excluded_dir in excluded_dirs):
        return True

    # Check if the file's name is in the excluded list
    if os.path.basename(file_path).lower() in [filename.lower() for filename in excluded_filenames]:
        return True

    return False

def handle_regex_error(file_path, regex_name, regex_error, output_file=None):
    """
    Handle errors that occur while applying regex patterns.

    Args:
        file_path (str): Path to the file.
        regex_name (str): Name of the regex pattern.
        regex_error (Exception): Error raised during regex operation.
        output_file (file): Output file to save error messages.
    """
    error_message = f"Error with regex '{regex_name}' in {file_path}: {str(regex_error)}"
    print(error_message)
    if output_file:
        output_file.write(error_message + "\n")

def search_directory(directory, excluded_extensions, excluded_dirs, excluded_filenames, output_directory, strip_chars=False):
    """
    Recursively search for files in a directory and apply search_file function to each file.

    Args:
        directory (str): Directory to search.
        excluded_extensions (list): List of extensions to exclude.
        excluded_dirs (list): List of directories to exclude.
        excluded_filenames (list): List of filenames to exclude.
        output_directory (str): Directory to save the output files.
        strip_chars (bool): Whether to strip bad characters from the results.
    """
    for root, dirs, files in os.walk(directory, topdown=True):
        # Modify dirs in place to avoid traversing into excluded directories
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in excluded_dirs]

        for file in files:
            file_path = os.path.join(root, file)
            if not should_skip_file(file_path, excluded_extensions, excluded_dirs, excluded_filenames):
                search_file(file_path, excluded_extensions, excluded_dirs, excluded_filenames, output_directory, strip_chars)

def main():
    parser = argparse.ArgumentParser(description="Search for sensitive data in files.")
    parser.add_argument("directory", help="Directory to search")
    parser.add_argument("-o", "--output", help="Output directory prefix to save results", default="output")
    parser.add_argument("-e", "--exclude_ext", help="File extensions to exclude (comma-separated, include dot)", default=".jpg,.png")
    parser.add_argument("-f", "--exclude_files", help="File names to exclude (comma-separated)", default="config.json,secrets.yml")
    parser.add_argument("-d", "--exclude_dirs", help="Directories to exclude (comma-separated, full path or relative to searched directory)", default="")
    parser.add_argument("-r", "--regex_dir", help="Directory containing regex .txt files", default="./regex")
    parser.add_argument("-s", "--strip_bad_chars", action='store_true', help="Strip unwanted characters from the match")
    args = parser.parse_args()

    excluded_extensions = args.exclude_ext.split(',') if args.exclude_ext else []
    excluded_filenames = args.exclude_files.split(',') if args.exclude_files else []
    # Include 'test', 'tests', 'testing', and any other directories specified by the user
    default_excluded_dirs = ["test", "tests", "testing",".git"]
    user_excluded_dirs = args.exclude_dirs.split(',') if args.exclude_dirs else []
    excluded_dirs = default_excluded_dirs + [dir for dir in user_excluded_dirs if dir not in default_excluded_dirs]

    output_directory = args.output
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Load regex patterns
    global general_regexes
    global language_specific_regexes
    
    general_regexes = load_regex_patterns(args.regex_dir)

    # Initialize the dictionary for language-specific regexes
    language_specific_regexes = {}
    
    # Assign the loaded regex patterns to each language based on the filenames
    for lang in file_type_map.values():
        language_specific_regexes[lang] = {
            name: regex for name, regex in general_regexes.items() if lang in name
        }

    search_directory(args.directory, excluded_extensions, excluded_dirs, excluded_filenames, output_directory, args.strip_bad_chars)

if __name__ == "__main__":
    main()
