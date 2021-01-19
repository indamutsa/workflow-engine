#######################################
# NODES
#######################################

class NumberNode: # It just take token of the float or number
    def __init__(self, token):
        self.token = token

        # Each node will have its position accordingly
        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end

    def __repr__(self):
        return f'{self.token}'


class BinOpNode: # It takes the left node, operator, and the right node
    def __init__(self, left_node, operator_token, right_node):
        self.left_node = left_node
        self.operator_token = operator_token
        self.right_node = right_node

        # We assign the position of the node. remember it is a tree, thus the position start from the left to the right 
        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.operator_token}, {self.right_node})'


class UnaryOperatorNode: # It takes the operator node, and the node to operate on (ex: number node or an expression)
    def __init__(self, operator_token, node):
        self.operator_token = operator_token
        self.node = node

        self.pos_start = self.operator_token.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f'({self.operator_token}, {self.node})'

class VarAccessNode: # This class takes care of the variable name
	def __init__(self, var_name_tok):
		self.var_name_tok = var_name_tok

        # We retrieve token position and assign to its node representation
		self.pos_start = self.var_name_tok.pos_start
		self.pos_end = self.var_name_tok.pos_end

class VarAssignNode: # The assignment of the value to the variable
    # We get the variable name and its assignment
	def __init__(self, var_name_tok, value_node): # Initialize them
		self.var_name_tok = var_name_tok
		self.value_node = value_node

        # the position start of the varible name to its value. from the left node which is the varible name to right node which is its value
		self.pos_start = self.var_name_tok.pos_start
		self.pos_end = self.value_node.pos_end
        

# This node gives us take care of the if statement. the cases(if, elif) and then the else_case 
class IfNode:
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case

        # Position of the node
        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (self.else_case or self.cases[len(self.cases) - 1])[0].pos_end


class ForNode: # This is the For node, everything it has such as step, keywords are all inside the node 
    def __init__(self, var_name_tok, start_value_node, end_value_node, step_value_node, body_node, should_return_null):
        self.var_name_tok = var_name_tok
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node # The content inside the loop
        self.should_return_null = should_return_null # This varible is a status in case we get a newline or nor

        # Position of the node
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.body_node.pos_end

class WhileNode: # while node reacts to statement as if statement but that loop until the condition is false 
    def __init__(self, condition_node, body_node,  should_return_null):
        self.condition_node = condition_node
        self.body_node = body_node
        self.should_return_null = should_return_null

        # Position of the node
        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end

# The function definition node, the signature and its body.
class FuncDefNode: 
    def __init__(self, var_name_tok, arg_name_toks, body_node, should_auto_return):
        self.var_name_tok = var_name_tok # The function might be anonymous
        self.arg_name_toks = arg_name_toks
        self.body_node = body_node
        self.should_auto_return = should_auto_return


        if self.var_name_tok:
            self.pos_start = self.var_name_tok.pos_start
        elif len(self.arg_name_toks) > 0: # In case it is an anonymous function, we willa also get the position
            self.pos_start = self.arg_name_toks[0].pos_start
        else:
            self.pos_start = self.body_node.pos_start

        self.pos_end = self.body_node.pos_end

# Another function to call
class CallNode:
	def __init__(self, node_to_call, arg_nodes):
		self.node_to_call = node_to_call
		self.arg_nodes = arg_nodes

		self.pos_start = self.node_to_call.pos_start

		if len(self.arg_nodes) > 0: # In case, it is an anonymous function, we willa also get the position
			self.pos_end = self.arg_nodes[len(self.arg_nodes) - 1].pos_end
		else:
			self.pos_end = self.node_to_call.pos_end

class StringNode:
	def __init__(self, token):
		self.token = token

		self.pos_start = self.token.pos_start
		self.pos_end = self.token.pos_end

	def __repr__(self):
		return f'{self.token}'


class ListNode:
    def __init__(self, element_nodes, pos_start, pos_end):
        self.element_nodes = element_nodes

        self.pos_start = pos_start
        self.pos_end = pos_end




class ReturnNode:
    def __init__(self, node_to_return, pos_start, pos_end):
        self.node_to_return = node_to_return

        self.pos_start = pos_start
        self.pos_end = pos_end

class ContinueNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end

class BreakNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end