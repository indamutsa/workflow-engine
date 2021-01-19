from app.errors.error import *
from app.interpreter.value import *
from app.interpreter.runtime_result import *
from app.tables.symbol import *
from app.lexer.lex_analyzer import *
from app.parser.parse import *
from app.interpreter.codeGen import *

import math,os


# This class execute the number logic using python
class Number(Value):

    def __init__(self, value):
        super().__init__()
        self.value = value



    def added_to(self, other):
        if isinstance(other, Number):
            # We are adding everything to the constructor and then return it
            return Number(self.value + other.value).setContext(self.context), None
        else:
            return None, Value.illegal_operation(self, other)


    def subbed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).setContext(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).setContext(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def dived_by(self, other):
        # pdb.set_trace()
        if isinstance(other, Number):
            if other.value == 0:
                return None, RunTimeError(
                    other.pos_start, other.pos_end,
                    'Division by zero',
                    self.context
                )

            return Number(self.value / other.value).setContext(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def exponented_by(self,other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).setContext(self.context), None
        else:
            return None, Value.illegal_operation(self, other)


    # Execute comparisons functions 
    # --------------------------------------------------------------------------------------
    def get_comparison_eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).setContext(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_ne(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).setContext(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).setContext(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).setContext(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).setContext(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).setContext(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def anded_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).setContext(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def ored_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).setContext(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def notted(self):
        return Number(1 if self.value == 0 else 0).setContext(self.context), None


    def is_true(self):
        return self.value != 0

    # --------------------------------------------------------------------------------------------

    # We can make copy of the current number node to keep track of ourselves
    def copy(self):
        copy = Number(self.value)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy

    def __repr__(self):
        return str(self.value)


class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name or "<anonymous>"

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent_node.symbol_table)
        return new_context

    def check_args(self, arg_names, args):
        res = RunTimeResult()

        if len(args) > len(arg_names):
            return res.failure(RunTimeError(
                self.pos_start, self.pos_end,
                f"{len(args) - len(arg_names)} too many args passed into {self}",
                self.context
            ))
        
        if len(args) < len(arg_names):
            return res.failure(RunTimeError(
                self.pos_start, self.pos_end,
                f"{len(arg_names) - len(args)} too few args passed into {self}",
                self.context
            ))

        return res.success(None)

    def populate_args(self, arg_names, args, exec_ctx):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]

            arg_value.setContext(exec_ctx)
            exec_ctx.symbol_table.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_ctx):
        res = RunTimeResult()

        res.runtimeFilter(self.check_args(arg_names, args))
        if res.should_return(): return res

        self.populate_args(arg_names, args, exec_ctx)
        return res.success(None)

class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names, should_auto_return):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
        self.should_auto_return = should_auto_return

    def execute(self, args):
        res = RunTimeResult()
        
        # pdb.set_trace()

        exec_context = self.generate_new_context()

        res.runtimeFilter(self.check_and_populate_args(self.arg_names, args, exec_context))
        if res.should_return(): return res


        return self.body_node, exec_context, self.should_auto_return

        # value = res.runtimeFilter(interpreter.visit(self.body_node, new_context))
        # if res.should_return(): return res
        # return res.success(value)

    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names, self.should_auto_return)
        copy.setContext(self.context)
        copy.setPosition(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<function {self.name}>"

Number.null = Number(0)
Number.false = Number(0)
Number.true = Number(1)
Number.math_PI = Number(math.pi)


class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)

    def execute(self, args):
        res = RunTimeResult()
        exec_ctx = self.generate_new_context()

        # Run time use of the method, we check the method to use at runtime
        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit_method)

        res.runtimeFilter(self.check_and_populate_args(method.arg_names, args, exec_ctx))
        if res.should_return(): return res

        return_value = res.runtimeFilter(method(exec_ctx))
        if res.should_return(): return res
        return res.success(return_value), exec_ctx, None 

    def no_visit_method(self, node, context):
        raise Exception(f'No execute_{self.name} method defined')

    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.setContext(self.context)
        copy.setPosition(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<built-in function {self.name}>"

    #####################################

    # Execute the print method
    def execute_display(self, exec_ctx):
        print(str(exec_ctx.symbol_table.get('value')))
        return RunTimeResult().success(Number.null)

    # We update the arguments passed in to print
    execute_display.arg_names = ['value']

    # This method return the value that will be printed
    def execute_display_return(self, exec_ctx):
        return RunTimeResult().success(String(str(exec_ctx.symbol_table.get('value'))))

    # We update the arguments passed in to print
    execute_display_return.arg_names = ['value']

    def execute_input(self, exec_ctx):
        text = input()
        return RunTimeResult().success(String(text))
    execute_input.arg_names = []

    def execute_input_int(self, exec_ctx):
        while True:
            text = input()
            try:
                number = int(text)
                break
            except ValueError:
                print(f"'{text}' must be an integer. Try again!")

        return RunTimeResult().success(Number(number))

    execute_input_int.arg_names = []

    def execute_clear(self, exec_ctx):
        os.system('cls' if os.name == 'nt' else 'clear') 
        return RunTimeResult().success(Number.null)

    execute_clear.arg_names = []

    def execute_is_number(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), Number)
        return RunTimeResult().success(Number.true if is_number else Number.false)
    execute_is_number.arg_names = ["value"]

    def execute_is_string(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), String)
        return RunTimeResult().success(Number.true if is_number else Number.false)
    execute_is_string.arg_names = ["value"]

    def execute_is_list(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), List)
        return RunTimeResult().success(Number.true if is_number else Number.false)
    execute_is_list.arg_names = ["value"]

    def execute_is_function(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), BaseFunction)
        return RunTimeResult().success(Number.true if is_number else Number.false)
    execute_is_function.arg_names = ["value"]

    def execute_append(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")
        value = exec_ctx.symbol_table.get("value")

        if not isinstance(list_, List):
            return RunTimeResult().failure(RTError(
            self.pos_start, self.pos_end,
            "First argument must be list",
            exec_ctx
            ))

        list_.elements.append(value)
        return RunTimeResult().success(Number.null)

    execute_append.arg_names = ["list", "value"]

    def execute_pop(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")
        index = exec_ctx.symbol_table.get("index")

        if not isinstance(list_, List):
            return RunTimeResult().failure(RTError(
            self.pos_start, self.pos_end,
            "First argument must be list",
            exec_ctx
            ))

        if not isinstance(index, Number):
            return RunTimeResult().failure(RTError(
            self.pos_start, self.pos_end,
            "Second argument must be number",
            exec_ctx
            ))

        try:
            element = list_.elements.pop(index.value)
        except:
            return RunTimeResult().failure(RTError(
            self.pos_start, self.pos_end,
            'Element at this index could not be removed from list because index is out of bounds',
            exec_ctx
            ))
        return RunTimeResult().success(element)

    execute_pop.arg_names = ["list", "index"]

    def execute_extend(self, exec_ctx):
        listA = exec_ctx.symbol_table.get("listA")
        listB = exec_ctx.symbol_table.get("listB")

        if not isinstance(listA, List):
            return RunTimeResult().failure(RTError(
            self.pos_start, self.pos_end,
            "First argument must be list",
            exec_ctx
            ))

        if not isinstance(listB, List):
            return RunTimeResult().failure(RTError(
            self.pos_start, self.pos_end,
            "Second argument must be list",
            exec_ctx
            ))

        listA.elements.extend(listB.elements)
        return RunTimeResult().success(Number.null)

    execute_extend.arg_names = ["listA", "listB"]

    # Calculate the length of list
    def execute_len(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")

        if not isinstance(list_, List) and not isinstance(list_, String):
            return RunTimeResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be list or string",
                exec_ctx
            ))

        if isinstance(list_, List):
            return RunTimeResult().success(Number(len(list_.elements)))

        return RunTimeResult().success(Number(len(list_.value)))

    execute_len.arg_names = ["list"]

    # def execute_run(self, exec_ctx):
    #     # We retrieve the filename
    #     fn = exec_ctx.symbol_table.get("filename")

    #     # We check if it is a string
    #     if not isinstance(fn, String):
    #         return RunTimeResult().failure(RTError(
    #         self.pos_start, self.pos_end,
    #         "Second argument must be string",
    #         exec_ctx
    #         ))
    #     # pdb.set_trace()
    #     # We get the value or the string itself
    #     filename = fn.value
    #     print(fn)

    #     # We read the file
    #     try:
    #         with open(filename, "r") as f:
    #             script_text = f.read()
    #     except Exception as e:
    #         return RunTimeResult().failure(RunTimeError(
    #             self.pos_start, self.pos_end,
    #             f"Failed to load script \"{fn}\"\n" + str(e),
    #             exec_ctx
    #         ))

    #     # Running the file
    #     # lexer = Lexer(filename, script_text)
    #     # tokens, error = lexer.generate_tokens()
    #     # print(tokens)

    #     # # Check if there is an error
    #     # if error: return None, error

    #     # # Generate the Abstract syntax tree 
    #     # parser = Parser(tokens)
    #     # tree = parser.parse()
    #     # if tree.error: return None, tree.error

    #     # # Traverse the tree and generate code, and run it
    #     # # interpreter = Interpreter()
    #     # context = Context('<program>')
    #     # context.symbol_table = global_symbol_table

    #     # # The result from the interpreter after visiting the abstract syntax tree and then generating and run the code with Python3
    #     # # import pdb; pdb.set_trace()
    #     # result = interpreter.visit(tree.node, context)



    #     # _, error = run(fn, script)

    #     # if error:
    #     #     return RunTimeResult().failure(RTError(
    #     #         self.pos_start, self.pos_end,
    #     #         f"Failed to finish executing script \"{fn}\"\n" +
    #     #         error.as_string(),
    #     #         exec_ctx
    #     #     ))

    #     return RunTimeResult().success(Number.null)

    # execute_run.arg_names = ["filename"]


BuiltInFunction.display       = BuiltInFunction("display")
BuiltInFunction.display_return   = BuiltInFunction("display_return")
BuiltInFunction.input       = BuiltInFunction("input")
BuiltInFunction.input_int   = BuiltInFunction("input_int")
BuiltInFunction.clear       = BuiltInFunction("clear")
BuiltInFunction.is_number   = BuiltInFunction("is_number")
BuiltInFunction.is_string   = BuiltInFunction("is_string")
BuiltInFunction.is_list     = BuiltInFunction("is_list")
BuiltInFunction.is_function = BuiltInFunction("is_function")
BuiltInFunction.append      = BuiltInFunction("append")
BuiltInFunction.pop         = BuiltInFunction("pop")
BuiltInFunction.extend      = BuiltInFunction("extend")
BuiltInFunction.len					= BuiltInFunction("len")
BuiltInFunction.run					= BuiltInFunction("run")



class String(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_to(self, other):
        if isinstance(other, String): # Concatenating the string
            return String(self.value + other.value).setContext(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other): # to multiply a string
        if isinstance(other, Number):
            return String(self.value * other.value).setContext(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def is_true(self):
        return len(self.value) > 0

    def copy(self):
        copy = String(self.value)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy

    def __repr__(self):
        return f'"{self.value}"'

    def __str__(self):
       return self.value 

class List(Value):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements

    # To be changed TODO
    def added_to(self, other):
        new_list = self.copy()
        new_list.elements.append(other)
        return new_list, None

    # To be changed TODO
    def subbed_by(self, other):
        if isinstance(other, Number):
            new_list = self.copy()
            try:
                new_list.elements.pop(other.value)
                return new_list, None
            except:
                return None, RunTimeError(
                    other.pos_start, other.pos_end,
                    'Element at this index could not be removed from list because index is out of bounds',
                    self.context
                )
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        if isinstance(other, List):
            new_list = self.copy()
            new_list.elements.extend(other.elements)
            return new_list, None
        else:
            return None, Value.illegal_operation(self, other)
    
    # To be changed TODO
    def dived_by(self, other):
        if isinstance(other, Number):
            try:
                return self.elements[other.value], None
            except:
                return None, RunTimeError(
                    other.pos_start, other.pos_end,
                    'Element at this index could not be retrieved from list because index is out of bounds',
                    self.context
                )
        else:
            return None, Value.illegal_operation(self, other)

    def copy(self):
        copy = List(self.elements)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy

    def __repr__(self):
        return f'[{", ".join([str(x) for x in self.elements])}]'

    def __str__(self):
        return f'{", ".join([str(x) for x in self.elements])}'