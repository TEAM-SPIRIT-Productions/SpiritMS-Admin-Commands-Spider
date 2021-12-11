# SpiritMS-Admin-Commands-Spider
This script crawls through the admin commands class in Swordie-like MapleStory private servers, to generate a list of admin commands available in the server.

This project is adapted from [ascii_checker](https://github.com/TEAM-SPIRIT-Productions/ascii_checker), which was initially made for filtering non-ASCII text from Azure v316 style source code (e.g. [ElectronMS](https://github.com/Bratah123/ElectronMS)).  

*Note: This script requires Python 3.6+, and is written/tested using Python 3.10*  

---

## How To Use  
1) Run `setup.bat` (optional, if you already have `ruamel.yaml` installed in your global Python environment)
    - This script creates a new virtual environment in the repository root, and installs all dependencies
2) Configure `config.py`  
    - E.g. `REPOSITORY_ROOT = "E:\Downloads\SpiritMS"`  
    - E.g. `DOCS = "E:\Downloads\SpiritSuite\SPIRITCOMMANDS.md"`  
3) Run `start.bat`  
4) Input whether to check admin commands list against SpiritSuite docs  
5) Check the `/output/` folder of this repository for the results
