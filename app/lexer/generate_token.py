#!/usr/bin/env python3

# Import
import json
from pathlib import Path



data_folder = Path("/home/arsene/Tools-Workspace/workflow-engine/app/utils")
file = data_folder / "tokentypes.json"

# Opening json file of token datas
f = open(file)
data = json.load(f)

print('var' in data['keywords'].values())
