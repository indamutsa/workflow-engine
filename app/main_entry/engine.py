# # This module will run the engine
from app.lexer.lex_analyzer import *
from app.parser.parse import *
from app.interpreter.traverser import *
from app.interpreter.runtime_result import *
from app.tables.symbol import *

from app.constants.constant import *

global_symbol_table = SymbolTable()
# We initialize it
global_symbol_table.set("null", Number.null)
global_symbol_table.set("true", Number.true)
global_symbol_table.set("false", Number.false)


global_symbol_table.set("MATH_PI", Number.math_PI)
global_symbol_table.set("display", BuiltInFunction.display)
global_symbol_table.set("display_retrun", BuiltInFunction.display_return)
global_symbol_table.set("input", BuiltInFunction.input)
global_symbol_table.set("input_int", BuiltInFunction.input_int)
global_symbol_table.set("clear", BuiltInFunction.clear)
global_symbol_table.set("cls", BuiltInFunction.clear)
global_symbol_table.set("is_num", BuiltInFunction.is_number)
global_symbol_table.set("is_str", BuiltInFunction.is_string)
global_symbol_table.set("is_list", BuiltInFunction.is_list)
global_symbol_table.set("is_function", BuiltInFunction.is_function)
global_symbol_table.set("append", BuiltInFunction.append)
global_symbol_table.set("pop", BuiltInFunction.pop)
global_symbol_table.set("extend", BuiltInFunction.extend)
global_symbol_table.set("size", BuiltInFunction.len)
global_symbol_table.set("run", BuiltInFunction.run)



# This function bootstraps(ignites) the workflow engine
def run_engine( filename, script_text):
    lexer = Lexer(filename, script_text)
    tokens, error = lexer.generate_tokens()

    # import pdb; pdb.set_trace()


    # Running the file:
    # In case what we get is file wrapped in run function, then we extract the text
    # Inside it and run them, otherwise, we grab the test from the terminal
    if tokens[0].type == 'identifier'  and tokens[0].value == 'run':
        # We read the file
        try:
            with open(tokens[2].value, "r") as f:
                script_text = f.read()
        except Exception as e:
            return RunTimeResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                f"Failed to load script \"{fn}\"\n" + str(e),
                exec_ctx
            ))

        lexer = Lexer(filename, script_text)
        tokens, error = lexer.generate_tokens()

    

    # Check if there is an error
    if error: return None, error

    # Generate the Abstract syntax tree 
    parser = Parser(tokens)
    tree = parser.parse()
    if tree.error: return None, tree.error

    # Traverse the tree and generate code, and run it
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table

    # The result from the interpreter after visiting the abstract syntax tree and then generating and run the code with Python3
    # import pdb; pdb.set_trace()
    result = interpreter.visit(tree.node, context)


    return result.value, result.error
