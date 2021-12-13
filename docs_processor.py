"""
Holds the functions for extracting useful data from the SpiritSuite docs.
"""

def extract_raw_commands(file_contents):
	"""
    Process a list of strings (representing the SPIRITCOMMANDS file contents),
    to extract any lines containing command aliases (and their required 
	permission level).
	
	Only lines ending with '**\\' followed by a line break will be extracted.
	This is to avoid duplicates, since the docs formats all mentions of commands
	using double asterisks, even when discussing formatting or usages.
    
    Args:
        List of strings
    Returns:
        A tuple of Lists representing different permission levels, containing 
		the commands and aliases associated with said permission levels.
    """
	# mode will determine which list being written to
	mode = 0
	player = []  # mode 0
	tester = []  # mode 1
	intern = []  # mode 2
	gamemaster = []  # mode 3
	admin = []  # mode 4
	
	for line in file_contents:
		if "## " in line:
			mode += 1
		if "## Player level commands:" in line:
			mode = 0
	
		if "**!" in line and "**\\\n" in line:
			if mode == 0:
				player.append(line)
			elif mode == 1:
				tester.append(line)
			elif mode == 2:
				intern.append(line)
			elif mode == 3:
				gamemaster.append(line)
			else:
				admin.append(line)

	return player, tester, intern, gamemaster, admin

def strip_formatting(lines):
	"""
	Strips the leading and trailing formatting symbols from the commands.
	
	Args:
		lines: List of Strings
	Returns:
		List of Strings
	"""
	return [line[3:-4] for line in lines]

def extract_commands(file_contents):
	"""
	Uses docs_processor::strip_formatting to clean up the commands
	"""
	raw_player, raw_tester, raw_intern, raw_gamemaster, raw_admin = extract_raw_commands(file_contents)
	player = strip_formatting(raw_player)
	tester = strip_formatting(raw_tester)
	intern = strip_formatting(raw_intern)
	gamemaster = strip_formatting(raw_gamemaster)
	admin = strip_formatting(raw_admin)
	
	return player, tester, intern, gamemaster, admin
	
def command_not_in_docs(command_aliases, permission_level):
	"""
	Checks if NONE of the command aliases specified is inside the docs
	
	Args:
		command_aliases: List of Strings
		permission_level: List of Strings
	Returns:
		Boolean, False if at least one command alias is in the docs
	"""
	for command in command_aliases:
		if command in permission_level:
			return False
	return True
