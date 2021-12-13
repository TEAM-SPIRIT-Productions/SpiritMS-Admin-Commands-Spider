"""Generates list of admin commands in Swordie-like repositories

This simple Python script crawls through the files inside the specified 
repository.
It creates a yaml file (with the list of admin commands) in the output folder.
If specified to check against the current docs, this script will also
generate a yaml file containing commands that are not already in the docs.
"""
from os import sys  # standard library
from pathlib import Path
import subprocess

from ruamel.yaml import YAML

import config
import logger  # local module (Spirit Logger)
import docs_processor


spirit_logger = logger.get_logger("main")
spirit_logger.info("Spirit Logger successfully loaded!")
yaml = YAML(typ="safe", pure=True)

# Set folder paths
input_dir = Path(config.REPOSITORY_ROOT, config.REPOSITORY_POSTFIX)
output_dir = Path(Path(), "output")
spirit_logger.debug(
    f"    Input directory: {input_dir}\n    Output directory: {output_dir}"
)
# sanity check:
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

configuration_check()

player = []
tester = []
intern = []
gamemaster = []
admin = []


def validate_input(option):
    """Just to make sure the script is fed with correct input"""
    if option in ("y", "n"):
        return
    spirit_logger.error(f"Invalid input: {option}, please use only 'y' or 'n'.")
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
    if not "{" in line:
        # sanity check for single-alias commands that don't follow conventions
        start = line.index(" \"") + 1
        end = line.index(",")
    else:
        try:
            start = line.index("{") + 1
            end = line.index("}")
        except ValueError as ve:
            spirit_logger.warning(f"Unable to process alias in line: {line}")
            spirit_logger.exception(ve, exc_info=True)
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
    return line[start:-2]


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


def get_target_by_permission_level(permission_level):
    """
    Get the target List, from the permission level property of a command.
    Requires the docs_processor::extract_commands function to be run, for
    the permission level lists to be populated.

    Args:
        permission_level: String
    Returns:
        List of Strings
    """
    if permission_level == "Player":
        return player
    elif permission_level == "Tester":
        return tester
    elif permission_level == "Intern":
        return intern
    elif permission_level == "GameMaster":
        return gamemaster
    else:
        return admin


def fetch_new_commands(extracted_commands):
    """
    Compares extracted commands against SpiritSuite docs contents,
    to find commands not inside of the docs, or have the wrong permission level.
    
    Args:
        extracted_commands: Dictionary of Dictionaries of Lists and Strings
    Returns:
        Dictionary of Dictionaries of Lists and Strings:
            {
                "Class Name": {
                    aliases: []
                    permission: ""
                }
            }
    """
    buffer = {}
    for class_name, metadata in extracted_commands.items():
        if docs_processor.command_not_in_docs(
            metadata["aliases"], 
            get_target_by_permission_level(metadata["permission"])
        ):
            buffer[class_name] = metadata
    return buffer
    
    
def permission_text(number):
    """
    To get the appropriate permission level text for each loop iteration
    in main::fetch_outdated_commands
    """
    if number == 0:
        return "Player Commands:\n"
    elif number == 1:
        return "Tester Commands:\n"
    elif number == 2:
        return "Intern Commands:\n"
    elif number == 3:
        return "GameMaster Commands:\n"
    else:
        return "Admin Commands:\n"
    
    
def fetch_outdated_commands(extracted_commands):
    """
    Compares extracted commands against SpiritSuite docs contents,
    to find entries in the docs that are outdated.
    
    Requires the docs_processor::extract_commands function to be run, for
    the permission level lists to be populated.
    
    Args:
        extracted_commands: Dictionary of Dictionaries of Lists and Strings
    Returns:
        List of Strings, representing aliases that have been removed
    """
    # First flatten the dictionary
    aliases = []
    for metadata in extracted_commands.values():
        aliases.extend(metadata["aliases"])
    
    docs_aliases = [player, tester, intern, gamemaster, admin]
    output = ["=== Outdated Aliases ==="]
    output.append("These are aliases in the SpiritSuite docs that are no longer part of the SpiritMS repository.\n")
    for index, level in enumerate(docs_aliases):
        output.append(permission_text(index))
        output.append("=====================")
        buffer = [command for command in level if not command in aliases]
        if buffer:
            output.extend(buffer)
            buffer.clear()
        else:
            output.append("NONE\n")
    
    return output


# Main sequence:
print("===== SpiritMS Admin Commands Spider =====")
option = input("Would you also like to check if there are admin commands that are not already in SpiritSuite? (y/n) ").lower()
validate_input(option)
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
    player, tester, intern, gamemaster, admin = \
        docs_processor.extract_commands(read_contents(get_docs_location()))
    spirit_logger.info("Checking for commands not inside of the docs, or that have the wrong permission level...")
    new_commands = fetch_new_commands(commands)
    spirit_logger.debug("New commands extracted, now dumping...")
    if new_commands:
        yaml.dump(new_commands, Path(output_dir, "NewCommands.yaml"))
    else:
        with open(Path(output_dir, "NewCommands.yaml"), mode="w", encoding="utf-8") as current_file:
            current_file.write("SpiritSuite docs is already up to date.")
    spirit_logger.info("New commands dumped.")
    spirit_logger.info("Checking for dead entries in the docs...")
    dead_commands = fetch_outdated_commands(commands)
    spirit_logger.debug("Dead commands extracted, now dumping...")
    with open(Path(output_dir, "DeadCommands.txt"), mode="w", encoding="utf-8") as current_file:
            current_file.write("\n".join(dead_commands))
    spirit_logger.info("Dead commands dumped.")

spirit_logger.info("Sequence completed! Check the output folder for the results.")
