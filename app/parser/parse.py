import pdb
from app.constants.constant import *
from app.ast.node import *
from app.parser.parseresult import *
from app.errors.error import *

# The parser build the tree of nodes from the tokens provided
# ******************************
#    Parser
#******************************* 

# Token types
_plus = TokenType['_plus']
_minus=  TokenType['_minus']
_div = TokenType['_div']
_mult = TokenType['_mult']
_int = TokenType['_int']
_float = TokenType['_float']
_end = TokenType['_eof']
lparen = TokenType['_lparen']
rparen = TokenType['_rparen']
_pow = TokenType['_pow']
keyword = TokenType['keyword']
identifier = TokenType['identifier']
_equal = TokenType['_eq']
db_eq = TokenType['_ee']
_ne = TokenType['_ne']
_lt = TokenType['_lt']
_lte = TokenType['_lte']
_gt = TokenType['_gt']
_gte = TokenType['_gte']
_comma = TokenType['_comma']
_arrow = TokenType['_arrow']
_string = TokenType['_string']
_lsquare = TokenType['_lsquare']
_rsquare = TokenType['_rsquare']
newline = TokenType['newline']

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_index = -1
        self.increment()

    def increment(self, ):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        return self.current_token

    def reverse(self, amountToReverse=1):
        self.token_index -= amountToReverse
        self.update_current_token()
        return self.current_token

    def update_current_token(self):
        if self.token_index >= 0 and self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]

    # The parser build the abstract syntax tree using parenthesis
    def parse(self):
        # pdb.set_trace()

        result = self.getStatements()

        # We have not yet reached the end of the file and the result has an error, we return the error
        if self.current_token.type != _end and not result.error:
            return result.failure(
                # We have detected invalid syntax
                InvalidSyntaxError( self.current_token.pos_start, self.current_token.pos_end,
                "Expected '+', '-', '*', '/', '^', '==', '!=', '<', '>', <=', '>=', 'and' or 'or'")
            )


        return result

    def getStatements(self):
        parsed_result = ParseFilter()
        statements = []
        pos_start = self.current_token.pos_start.copy()

        while self.current_token.type == newline:
            parsed_result.register_advancement()
            self.increment()

        statement = parsed_result.filterError(self.getStatement())
        if parsed_result.error: return parsed_result
        statements.append(statement)

        more_statements = True

        while True:

            newline_count = 0
            
            while self.current_token.type == newline:
                parsed_result.register_advancement()
                self.increment()
                newline_count += 1

            if newline_count == 0:
                more_statements = False
                
            if not more_statements: break
            
            statement = parsed_result.registerStatement(self.getStatement())
            if not statement:
                self.reverse(parsed_result.to_reverse_count)
                more_statements = False
                continue
            statements.append(statement)

        return parsed_result.success(ListNode(
            statements,
            pos_start,
            self.current_token.pos_end.copy()
        ))

    def getStatement(self):
        parsed_result = ParseFilter()
        pos_start = self.current_token.pos_start.copy()

        if self.current_token.matches(keyword, 'return'):
            parsed_result.register_advancement()
            self.increment()

            expr = parsed_result.registerStatement(self.getExpression())
            if not expr:
               self.reverse(parsed_result.to_reverse_count)
            return parsed_result.success(ReturnNode(expr, pos_start, self.current_token.pos_start.copy()))

        if self.current_token.matches(keyword, 'continue'):
            parsed_result.register_advancement()
            self.increment()
            return parsed_result.success(ContinueNode(pos_start, self.current_token.pos_start.copy()))
            
        if self.current_token.matches(keyword, 'break'):
            parsed_result.register_advancement()
            self.increment()
            return parsed_result.success(BreakNode(pos_start, self.current_token.pos_start.copy()))

        expression = parsed_result.filterError(self.getExpression())

        if parsed_result.error:
            return parsed_result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected 'return', 'continue', 'break', 'var', 'if', 'for', 'while', 'function', int, float, identifier, '+', '-', '(', '[' or 'not'"
            ))

        return parsed_result.success(expression)

    def getExpression(self):  # var var_name = expression ===> this is the logic we are implementing

        parsed_result = ParseFilter()

        # We look for the keyword var, when we find it, we continue by both incrementing and registering our advancement
        if self.current_token.matches(keyword, 'var'):
            parsed_result.register_advancement()
            self.increment()

            # If the current token type is not an identifier, such as variable
            if self.current_token.type != identifier:
                return parsed_result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected identifier(such as variable name)"
                ))

            # Otherwise when we find the variable name, we assign to the var name and advance to find EQUALS
            var_name = self.current_token
            parsed_result.register_advancement()
            self.increment()

            # If the next value is not equal, there is a problem
            if self.current_token.type != _equal:
                return parsed_result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected '='"
                ))

            # We register our advancement and then we increment to find the expression which is essentially the value of the variable
            parsed_result.register_advancement()
            self.increment()

            # This expression will be assigned to the variable. Expression can be a factor(2, 6, ..), a term (3 + 5), a combination and so on
            expression = parsed_result.filterError(self.getExpression())
            if parsed_result.error: return parsed_result

            # We assign the value by making specific node for assignment
            return parsed_result.success(VarAssignNode(var_name, expression))

        # if the current token is not a var keyword, then we recursively call the rest of functons.
        # The returned result needs to be screened to check if there was no error
        node = parsed_result.filterError(self.binary_operation(self.getComparisonExpression, ((keyword, 'and'), (keyword, 'or'))))

        # If there was an error, we return it accordingly
        if parsed_result.error:
            return parsed_result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected 'var', 'if, 'for', 'while', 'function', int, float, identifier, '+', '-' or '(', '['"
            ))

        return parsed_result.success(node)

    def getComparisonExpression(self):
        parsed_result = ParseFilter()

        if self.current_token.matches(keyword, 'not'):
            operator_token = self.current_token
            parsed_result.register_advancement()
            self.increment()

            node = parsed_result.filterError(self.getComparisonExpression())
            if parsed_result.error: return parsed_result
            return parsed_result.success(UnaryOperatorNode(operator_token, node))
        
        node = parsed_result.filterError(self.binary_operation(self.getArithmeticExpression, (db_eq, _ne, _lt, _gt, _lte, _gte)))
        
        if parsed_result.error:
            return parsed_result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected int, float, identifier, '+', '-', '(','[', or 'NOT'"
            ))

        return parsed_result.success(node)  

    def getArithmeticExpression(self):
        return self.binary_operation(self.getTerm, (_plus, _minus))

    def getTerm(self):
        return self.binary_operation(self.getFactor, (_mult, _div))

    # ----------------------------------------------------------------
    # second smallest 
    def getFactor(self):
        # pdb.set_trace()
        parsed_result = ParseFilter()
        token = self.current_token

        # Now our factor can have an unary operator
        if token.type in (_plus, _minus):

            parsed_result.register_advancement()
            self.increment()

            # We retrieve the factor, in this case number recursively. It will call itself and will skip
            # the check of operator minus and plus
            factor = parsed_result.filterError(self.getFactor())

            if parsed_result.error: return parsed_result
            return parsed_result.success(UnaryOperatorNode(token, factor))

        return self.power()

    # Implementing the power method
    def power(self):
        return self.binary_operation(self.call, (_pow, ), self.getFactor)

    # This function calls another function inside that function
    def call(self):
        parsed_result = ParseFilter()

        # We retrieve result from the atom which are usually factors with operators, but also with the for if while nodes 
        atom = parsed_result.filterError(self.getAtom())
        if parsed_result.error: return parsed_result

        if self.current_token.type == lparen:
            parsed_result.register_advancement()
            self.increment()
            arg_nodes = [] # argument nodes

            if self.current_token.type == rparen:
                parsed_result.register_advancement()
                self.increment()
            else:
                arg_nodes.append(parsed_result.filterError(self.getExpression()))
                if parsed_result.error:
                    return parsed_result.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "Expected ')', 'var', 'if', 'for', 'while', 'fun', int, float, identifier, '+', '-', '(', '[', or 'not'"
                    ))

                # Adding arguments into arguments list nodes
                while self.current_token.type == _comma:
                    parsed_result.register_advancement()
                    self.increment()

                    arg_nodes.append(parsed_result.filterError(self.getExpression())) # However the argument nodes are expression nodes
                    if parsed_result.error: return parsed_result

                if self.current_token.type != rparen:
                    return parsed_result.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        f"Expected ',' or ')'"
                    ))

                parsed_result.register_advancement()
                self.increment()

            return parsed_result.success(CallNode(atom, arg_nodes))
        return parsed_result.success(atom)

    def getAtom(self):

        # pdb.set_trace()
        parsed_result = ParseFilter()
        token = self.current_token

        # We are going through the list, if we get one of these operations, that means that
        # The next node is a number node, thus we increment to get it
        if token.type in (_int, _float):
            parsed_result.register_advancement()
            self.increment()
            return parsed_result.success( NumberNode(token))

        # Building the string node
        elif token.type == _string:
            parsed_result.register_advancement()
            self.increment()
            return parsed_result.success(StringNode(token))

        # We check for the variable to assign if it is there
        elif token.type == identifier:
            parsed_result.register_advancement()
            self.increment()
            return parsed_result.success(VarAccessNode(token))


        elif token.type == lparen:

            parsed_result.register_advancement()
            self.increment()

            # When we find a left parenthesis. this means there is an expression, we call the expression 
            # to get the expression. The expression is made term and factor recursively
            expression = parsed_result.filterError(self.getExpression())

            if parsed_result.error: return parsed_result

            # When we arrive at the right parenthesis, we can return the expression
            if self.current_token.type == rparen:
                
                parsed_result.register_advancement()
                self.increment()
                
                return parsed_result.success(expression)
            
            else: # otherwise there is an error
                return parsed_result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected ')'"
                ))

        # The list expression
        elif token.type == _lsquare:
            listExpression = parsed_result.filterError(self.getListExpression())
            if parsed_result.error: return parsed_result
            return parsed_result.success(listExpression)


        # If in the atomic function we find if, we build an if node
        elif token.matches(keyword, 'if'): 
            ifExpression = parsed_result.filterError(self.getIfExpression())
            if parsed_result.error: return parsed_result
            return parsed_result.success(ifExpression)

        # If in the atomic function we find for, we build an if node
        elif token.matches(keyword, 'for'):
            forExpression = parsed_result.filterError(self.getForExpression())
            if parsed_result.error: return parsed_result
            return parsed_result.success(forExpression)

        # If in the atomic function we find while, we build an if node
        elif token.matches(keyword, 'while'):
            whileExpression = parsed_result.filterError(self.getWhileExpression())
            if parsed_result.error: return parsed_result
            return parsed_result.success(whileExpression)

        elif token.matches(keyword, 'function'):
            func_def = parsed_result.filterError(self.getFuncdef())
            if parsed_result.error: return parsed_result
            return parsed_result.success(func_def)

        return parsed_result.failure(
                # We have detected invalid syntax
                InvalidSyntaxError( self.current_token.pos_start, self.current_token.pos_end,
                "Expected 'int', 'float', 'identifier', '+' or '-', or '(', '[', 'if, 'for', 'while', 'function'")
            )

    def getListExpression(self):
        parsed_result = ParseFilter()
        
        # Element nodes in our list
        element_nodes = []

        pos_start = self.current_token.pos_start.copy()

        if self.current_token.type != _lsquare:
            return parsed_result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected '['"
            ))

        parsed_result.register_advancement()
        self.increment()

        if self.current_token.type == _rsquare:
            parsed_result.register_advancement()
            self.increment()
        else:
            element_nodes.append(parsed_result.filterError(self.getExpression()))

            if parsed_result.error:
                return parsed_result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected ']', 'var', 'if', 'for', 'while', 'function', int, float, identifier, '+', '-', '(', '[' or 'not'"
                ))

            while self.current_token.type == _comma:
                parsed_result.register_advancement()
                self.increment()

                element_nodes.append(parsed_result.filterError(self.getExpression()))
                if parsed_result.error: return parsed_result

            if self.current_token.type != _rsquare:
                return parsed_result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    f"Expected ',' or ']'"
                ))

            parsed_result.register_advancement()
            self.increment()

        return parsed_result.success(ListNode(
                element_nodes,
                pos_start,
                self.current_token.pos_end.copy()
            ))

    def getIfExpression(self):
        parsed_result = ParseFilter()
        all_cases = parsed_result.filterError(self.getIfExpressionCases('if'))

        if parsed_result.error: return parsed_result

        cases, else_case = all_cases
        return parsed_result.success(IfNode(cases, else_case))

    def getElifExpression(self):
        return self.getIfExpressionCases('elif')

    def getElseExpression(self):
        parsed_result = ParseFilter()
        else_case = None

        if self.current_token.matches(keyword, 'else'):
            parsed_result.register_advancement()
            self.increment()

            if self.current_token.type == newline:
                parsed_result.register_advancement()
                self.increment()

                statements = parsed_result.filterError(self.getStatements())
                if parsed_result.error: return parsed_result
                else_case = (statements, True)

                if self.current_token.matches(keyword, 'end'):
                    parsed_result.register_advancement()
                    self.increment()
                else:
                    return parsed_result.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "Expected 'end'"
                    ))
            else:
                expr = parsed_result.filterError(self.getStatement())
                if parsed_result.error: return parsed_result
                else_case = (expr, False)

        return parsed_result.success(else_case)

    def getElifOrEleseExpression(self):
        parsed_result = ParseFilter()
        cases, else_case = [], None

        if self.current_token.matches(keyword, 'elif'):
            all_cases = parsed_result.filterError(self.getElifExpression())
            if parsed_result.error: return parsed_result
            cases, else_case = all_cases
        else:
            else_case = parsed_result.filterError(self.getElseExpression())
            if parsed_result.error: return parsed_result

        return parsed_result.success((cases, else_case))

    def getIfExpressionCases(self, case_keyword):
        parsed_result = ParseFilter()
        cases = []
        else_case = None

        if not self.current_token.matches(keyword, case_keyword):
            return parsed_result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected '{case_keyword}'"
            ))

        parsed_result.register_advancement()
        self.increment()

        condition = parsed_result.filterError(self.getExpression())
        if parsed_result.error: return parsed_result

        if not self.current_token.matches(keyword, 'then'):
            return parsed_result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'then'"
            ))

        parsed_result.register_advancement()
        self.increment()

        if self.current_token.type == newline:
            parsed_result.register_advancement()
            self.increment()

            statements = parsed_result.filterError(self.getStatements())
            
            if parsed_result.error: return parsed_result
            cases.append((condition, statements, True))

            if self.current_token.matches(keyword, 'end'):
                parsed_result.register_advancement()
                self.increment()
            else:
                all_cases = parsed_result.filterError(self.getElifOrEleseExpression())
                if parsed_result.error: return parsed_result
                new_cases, else_case = all_cases
                cases.extend(new_cases)
        else:
            expr = parsed_result.filterError(self.getStatement())
            if parsed_result.error: return parsed_result
            cases.append((condition, expr, False))

            all_cases = parsed_result.filterError(self.getElifOrEleseExpression())
            if parsed_result.error: return parsed_result
            new_cases, else_case = all_cases
            cases.extend(new_cases)

        return parsed_result.success((cases, else_case))

    def getForExpression(self):
        # pdb.set_trace()
        parsed_result = ParseFilter()

        if not self.current_token.matches(keyword, 'for'):
            return parsed_result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'for'"
            ))

        parsed_result.register_advancement()
        self.increment()

        if self.current_token.type != identifier:
            return parsed_result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected identifier"
            ))

        var_name = self.current_token
        parsed_result.register_advancement()
        self.increment()

        if self.current_token.type != _equal:
            return parsed_result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected '='"
            ))
        
        parsed_result.register_advancement()
        self.increment()

        start_value = parsed_result.filterError(self.getExpression())
        if parsed_result.error: return parsed_result

        if not self.current_token.matches(keyword, 'to'):
            return parsed_result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'to'"
            ))
        
        parsed_result.register_advancement()
        self.increment()

        end_value = parsed_result.filterError(self.getExpression())
        if parsed_result.error: return parsed_result

        if self.current_token.matches(keyword, 'step'):
            parsed_result.register_advancement()
            self.increment()

            step_value = parsed_result.filterError(self.getExpression())
            if parsed_result.error: return parsed_result
        else:
            step_value = None

        if not self.current_token.matches(keyword, 'then'):
            return parsed_result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'then'"
            ))

        parsed_result.register_advancement()
        self.increment()

        if self.current_token.type == newline:
            parsed_result.register_advancement()
            self.increment()

            body = parsed_result.filterError(self.getStatements())
            if parsed_result.error: return parsed_result

            if not self.current_token.matches(keyword, 'end'):
                return parsed_result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    f"Expected 'end'"
                ))
            
            parsed_result.register_advancement()
            self.increment()

            return parsed_result.success(ForNode(var_name, start_value, end_value, step_value, body, True))

        body = parsed_result.filterError(self.getStatement())
        if parsed_result.error: return parsed_result

        return parsed_result.success(ForNode(var_name, start_value, end_value, step_value, body, False))

    def getWhileExpression(self):
        parsed_result = ParseFilter()

        if not self.current_token.matches(keyword, 'while'):
            return parsed_result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'while'"
            ))

        parsed_result.register_advancement()
        self.increment()

        condition = parsed_result.filterError(self.getExpression())
        if parsed_result.error: return parsed_result

        if not self.current_token.matches(keyword, 'then'):
            return parsed_result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'then'"
            ))

        parsed_result.register_advancement()
        self.increment()

        if self.current_token.type == newline:
            parsed_result.register_advancement()
            self.increment()

            body = parsed_result.filterError(self.getStatements())
            if parsed_result.error: return parsed_result

            if not self.current_token.matches(keyword, 'end'):
                return parsed_result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    f"Expected 'end'"
                ))
            
            parsed_result.register_advancement()
            self.increment()

            return parsed_result.success(WhileNode(condition, body, True))

        body = parsed_result.filterError(self.getStatement())
        if parsed_result.error: return parsed_result

        return parsed_result.success(WhileNode(condition, body, False))

    def getFuncdef(self):
        parsed_result = ParseFilter()

        if not self.current_token.matches(keyword, 'function'):
            return parsed_result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'function'"
            ))

        parsed_result.register_advancement()
        self.increment()

        if self.current_token.type == identifier:
            var_name_tok = self.current_token
            parsed_result.register_advancement()
            self.increment()
            if self.current_token.type != lparen:
                return parsed_result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    f"Expected '('"
                ))
        else:
            var_name_tok = None
            if self.current_token.type != lparen:
                return parsed_result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    f"Expected identifier or '('"
                ))
        
        parsed_result.register_advancement()
        self.increment()
        arg_name_toks = [] # To hold the arguments

        if self.current_token.type == identifier:
            arg_name_toks.append(self.current_token)
            parsed_result.register_advancement()
            self.increment()
            
            while self.current_token.type == _comma:
                parsed_result.register_advancement()
                self.increment()

                if self.current_token.type != identifier:
                    return parsed_result.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        f"Expected identifier"
                    ))

                arg_name_toks.append(self.current_token)
                parsed_result.register_advancement()
                self.increment()
            
            if self.current_token.type != rparen:
                return parsed_result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    f"Expected ',' or ')'"
                ))
        else:
            if self.current_token.type != rparen:
                return parsed_result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    f"Expected identifier or ')'"
                ))

        parsed_result.register_advancement()
        self.increment()

        # If there is an arrow
        if self.current_token.type == _arrow:

            parsed_result.register_advancement()
            self.increment()

            # The node we are returning, it is an expression
            node_to_return = parsed_result.filterError(self.getExpression())
            if parsed_result.error: return parsed_result

            return parsed_result.success(FuncDefNode(
                var_name_tok,
                arg_name_toks,
                node_to_return,
                True
            ))

        # If there is a newline
        if self.current_token.type != newline:
            return parsed_result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected '->' or newline"
            ))

        parsed_result.register_advancement()
        self.increment()

        body = parsed_result.filterError(self.getStatements())
        if parsed_result.error: return res

        if not self.current_token.matches(keyword, 'end'):
            return parsed_result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'end'"
            ))

        parsed_result.register_advancement()
        self.increment()

        return parsed_result.success(FuncDefNode(
            var_name_tok,
            arg_name_toks,
            body,
            False
        ))

    # So this function can gets the right and the left and the operator from the list of tokens
	# It is a generic function for both the factor and getTerm function
    def binary_operation(self, func_a, operator_lists, func_b=None):

        if not func_b: func_b = func_a

        parsed_result = ParseFilter()

        # We look for the left node in list, and we insert that in the tree
        left = parsed_result.filterError(func_a())
        
        # If there is an error 
        if parsed_result.error:
            return parsed_result

        # As long as we still have the operators, we have the term(ex: 2 - 5)
        while self.current_token.type in operator_lists or (self.current_token.type, self.current_token.value) in operator_lists:

            operation_tok = self.current_token
            
            # We increment and register our current location in the text
            parsed_result.register_advancement()
            self.increment()

            # We look for the right node to insert it in the tree, because we have already visited the left node above. 
            right = parsed_result.filterError(func_b())


            # If there is an error 
            if parsed_result.error:
                return parsed_result


            # This node which has left, right node and the operator are placed (inserted) in the tree 
            # as a left node
            left = BinOpNode(left, operation_tok, right)

        return parsed_result.success(left)




