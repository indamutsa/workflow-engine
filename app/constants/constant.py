#!/usr/bin/env python3

# In this class we define all constants that will be reused across the program
import string, json, math
from pathlib import Path

# These are constants that are needed by our language execution
digits = string.digits 
letters = string.ascii_letters 
letters_digits = letters + digits 




data_folder = Path("/home/arsene/Tools-Workspace/workflow-engine/app/utils")
file = data_folder / "tokentypes.json"

# Opening json file of token datas
f = open(file)

# The data contains the token type and keywords
TokenType = json.load(f)

