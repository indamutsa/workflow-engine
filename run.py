#!/usr/bin/env python3 
# ------ We are ensuring that the underlying system run python 3 ------

# from app import create_app

# # This is our app
# workflow = create_app()


# if __name__ == '__main__':
#     workflow.run(debug=True, host='0.0.0.0')

# ####################################################################


import pdb
from app.main_entry.engine import *


# This is the entry of and enable us to interact with the program
while True:
    script_text = input('Workflow engine: >>>  ')
    
    # In case the value entered is empty, continue
    if script_text.strip() == "":
        continue

    result, error = run_engine('<stdin>', script_text)
    
    if error: print(error.tracebackError())
    elif result: 
        if len(result.elements) == 1:
            print(repr(result.elements[0]))
        else:
            print(repr(result))
