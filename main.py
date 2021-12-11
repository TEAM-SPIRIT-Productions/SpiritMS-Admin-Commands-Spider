"""Generates list of admin commands in Swordie-like repositories

This simple Python script crawls through the files inside the specified 
repository.
It creates a yaml file (with the list of admin commands) in the output folder.
If specified to check against the current docs, this script will also
generate a yaml file containing commands that are not already in the docs.
"""
from pathlib import Path  # standard library
import subprocess

from ruamel.yaml import YAML

import config
import logger  # local module (Spirit Logger)


spirit_logger = logger.get_logger("main")
spirit_logger.info("Spirit Logger successfully loaded!")
yaml = YAML(typ="safe", pure=True)

# Set folder paths
input_dir = Path(config.REPOSITORY_ROOT, REPOSITORY_POSTFIX)
output_dir = Path(Path(), "output")
spirit_logger.debug(
    f"    Input directory: {input_dir}\n    Output directory: {output_dir}"
)
# sanity check:
configuration_check()


def configuration_check():
    """Enforce repository location setting.
    """
    if config.REPOSITORY_ROOT and input_dir.is_dir() and output_dir.is_dir():
        return
    if config.DOCS:  # if local docs specified, check if it's valid
        if Path(config.DOCS).is_file():
            return
    spirit_logger.error("Configuration errors found!")
    spirit_logger.error("Could not access one or more I/O folders - please check the target repositories in config.py, and/or re-clone this repository.")
    logger.shutdown_logger()
    sys.exit("SpiritMS Admin Commands Spider has been terminated.")


def get_docs_location():
    """Fetches the location of the SpiritSuite docs
    
    Uses the local docs if one is provided in config.py
    Else, check if a local cached copy exists (and provide the cached copy).
    Else, use wget to fetch a copy to cache.
    
    Returns:
        Path object, representing the file path
    """
    if config.DOCS:  # if configured
        return Path(config.DOCS)
    # if docs location not configured:
    spirit_logger.info("No local docs location configured.")
    buffer = Path(Path(), "SPIRITCOMMANDS.md")
    if not buffer.is_file():  # no local caches
        spirit_logger.info("No local docs cache found. Downloading from GitHub.")
        result = subprocess.run(
            [
                "wget", 
                "--no-cache", 
                "--backups=1", 
                "https://raw.githubusercontent.com/KOOKIIEStudios/SpiritSuite/main/SPIRITCOMMANDS.md",
            ], 
            stderr=subprocess.PIPE, 
            stdout=subprocess.PIPE
        )
        spirit_logger.debug(result.stderr.decode("utf-8"))
    spirit_logger.info("Loading docs from local cache.")
    return buffer


def read_contents(file_path):
    """
    Wrapper for in-built file open

    Args:
        file_path: String, representing the file path
    Returns:
        List of Strings, representing file contents.
        Each element in the list is a line in the file
    """
    spirit_logger.debug(f"    Reading the contents of: {file_path}")
    try:
        with open(file_path, mode="r", encoding="utf-8") as current_file:
            file_contents = current_file.readlines()
    except:
        spirit_logger.warning(
            f"      File is NOT UTF-8! Flagging file: {file_path}"
        )
    if not file_contents:
        spirit_logger.warning(f"    Could not process: {file_path}")
    return file_contents


def contains_command(line):
    """
    Checks if a string contains the substring '@Command('. If so, return True.
    Else, return False.
    
    Args:
        String
        
    Returns:
        Boolean
    """
    if "@Command(" in line:
        return True
    return False


def extract_class_name(line):
    """
    Extract the class name from a line containing one.
    
    Args:
        line: String, representing a line of code
    Returns:
        String, representing the class name
    """
    substring_index = line.index("class") + 6
    buffer = line[substring_index:].split(" ")
    return buffer[0]


def extract_aliases(line):
    """
    Extract the command aliases from a line containing them.
    
    Args:
        line: String, representing a line of code
    Returns:
        List of Strings, representing the aliases
    """
    start = line.index("{") + 1
    end = line.index("}")
    return line[start:end].replace("\"", "").split(", ")


def extract_permission_level(line):
    """
    Extract the command permission level from a line containing it.
    
    Args:
        line: String, representing a line of code
    Returns:
        String, representing the permission level required to execute the command
    """
    start = line.index(".") + 1
    return line[start:-1]


def extract_commands(file_contents):
    """
    Process a list of strings (representing the AdminCommands file contents),
    to extract all commands (and their required permission level)
    
    Args:
        List of strings
    Returns:
        Dictionary of Dictionaries of Lists and Strings: 
            {
                "Class Name": {
                    aliases: []
                    permission: ""
                }
            }
    """
    output_buffer = {}
    if not file_contents:  # empty files
        spirit_logger.debug("    Unparseable file skipped")
        return
        
    for index, line in enumerate(file_contents):
        if contains_command(line):
            name = extract_class_name(file_contents[index+1])
            output_buffer[name] = {}
            output_buffer[name]["aliases"] = extract_aliases(line)
            output_buffer[name]["permission"] = extract_permission_level(line)
    
    return output_buffer


# Main sequence:
print("===== SpiritMS Admin Commands Spider =====")
option = input("Would you also like to check if there are admin commands that are not already in SpiritSuite? (y/n) ").lower()
spirit_logger.info(f"     Check against SpiritSuite docs: {option == 'y'}")

# First extact the admin commands into a dictionary
spirit_logger.info("Now extracting admin commands...")
commands = extract_commands(read_contents(input_dir))
spirit_logger.debug("Admin commands extracted, now dumping...")
yaml.dump(commands, Path(output_dir, "AdminCommands.yaml"))
spirit_logger.info("Admin commands dumped.")

# Then check for differences against SpiritSuite, if desired
if option == "y":
    spirit_logger.info("Checking for differences against SpiritSuite...")
    # TODO: Fill in logic
    spirit_logger.info("Differences checked.")

spirit_logger.info("Sequence completed!")
