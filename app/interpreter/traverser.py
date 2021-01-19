import pdb
from app.constants.constant import *
from app.interpreter.runtime_result import *
from app.interpreter.codeGen import *



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

# This class traverses the tree of nodes from the tokens provided
# ******************************
#   Interpreter
#******************************* 

class Interpreter:

	# This method is generic and visit the tree and interpretes it into executable
	def visit(self, node, context):
        # We retrieve the visit method at runtime
        # We get the method name according to the passed node
		# pdb.set_trace()
		method_name = f'visit_{type(node).__name__}'
        
        # Then we give its attributes, we also pass no method when no node is passed
		method = getattr(self, method_name, self.no_visit_method)
		return method(node, context)

	# When no visit method is available
	def no_visit_method(self, node, context):
		raise Exception(f'No visit_{type(node).__name__} method defined')


	def visit_NumberNode(self, node, context):
		return RunTimeResult().success(
			Number(node.token.value).setContext(context).setPosition(node.pos_start, node.pos_end)
		)

	def visit_StringNode(self, node, context):
		return RunTimeResult().success(
			String(node.token.value).setContext(context).setPosition(node.pos_start, node.pos_end)
		)


	def visit_ListNode(self, node, context):
		res = RunTimeResult()
		elements = []

		for element_node in node.element_nodes:
			elements.append(res.runtimeFilter(self.visit(element_node, context)))
			if res.should_return(): return res

		return res.success(
			List(elements).setContext(context).setPosition(node.pos_start, node.pos_end)
		)

    # On the Binary Operator Node, what we need to visit both the right and the left child node
	def visit_BinOpNode(self, node, context):
		result = RunTimeResult()

        # The method used in visiting the node is Post Order tree traversal
        # Link here (https://www.geeksforgeeks.org/tree-traversals-inorder-preorder-and-postorder/)

        # Visit the left node
		left = result.runtimeFilter(self.visit(node.left_node, context))
		if result.should_return(): return result


        # Visit the right child node
		right = result.runtimeFilter(self.visit(node.right_node, context))
		if result.should_return(): return result

        # Check the node so that we perform operations
		if node.operator_token.type == _plus:
			operation_result, error = left.added_to(right)
		elif node.operator_token.type == _minus:
			operation_result, error = left.subbed_by(right)
		elif node.operator_token.type == _mult:
			operation_result, error = left.multed_by(right)
		elif node.operator_token.type == _div:
			operation_result, error = left.dived_by(right)
		elif node.operator_token.type == _pow:
			operation_result, error = left.exponented_by(right)
		elif node.operator_token.type == db_eq:
			operation_result, error = left.get_comparison_eq(right)
		elif node.operator_token.type == _ne:
			operation_result, error = left.get_comparison_ne(right)
		elif node.operator_token.type == _lt:
			operation_result, error = left.get_comparison_lt(right)
		elif node.operator_token.type == _gt:
			operation_result, error = left.get_comparison_gt(right)
		elif node.operator_token.type == _lte:
			operation_result, error = left.get_comparison_lte(right)
		elif node.operator_token.type == _gte:
			operation_result, error = left.get_comparison_gte(right)
		elif node.operator_token.matches(keyword, 'and'):
			operation_result, error = left.anded_by(right)
		elif node.operator_token.matches(keyword, 'or'):
			operation_result, error = left.ored_by(right)

		if error:
			return result.failure(error)
		else:
			return result.success(operation_result.setPosition(node.pos_start, node.pos_end))

    # We visit the unary operator node
	def visit_UnaryOperatorNode(self, node, context):
		result = RunTimeResult()
		number = result.runtimeFilter(self.visit(node.node, context))
		if result.should_return(): return result

		error = None

        # If the node has a unary operator which is minus, we multiply negative one by the node
		if node.operator_token.type == _minus:
			number, error = number.multed_by(Number(-1))

        
		if error:
			return result.failure(error)
		else:
			return result.success(number.setPosition(node.pos_start, node.pos_end))

	# We can visit variable name node
	def visit_VarAccessNode(self, node, context):
		res = RunTimeResult()

		# Get the variable name from var access node
		var_name = node.var_name_tok.value

		# The context is coming table as context, with global variables that can be accessed anywhere in code
		value = context.symbol_table.get(var_name)

		if not value:
			return res.failure(RunTimeError(
				node.pos_start, node.pos_end,
				f"'{var_name}' is not defined",
				context
			))

		# If we get variable name, we make a copy of the name to keep its track and then we continue
		value = value.copy().setPosition(node.pos_start, node.pos_end).setContext(context)
		return res.success(value)

	# We can visit the variable assignment node. Remember this node has the variable name and the value assigned to it
	def visit_VarAssignNode(self, node, context):
		res = RunTimeResult()
		var_name = node.var_name_tok.value

		# We filter the value to see if there was no error
		value = res.runtimeFilter(self.visit(node.value_node, context))
		if res.should_return(): return res

		# We update our symbol table by assigning the variable name and the value
		context.symbol_table.set(var_name, value)
		return res.success(value)


	def visit_IfNode(self, node, context):
		result = RunTimeResult()

		# From if node or sub-tree, we have the node, and content 
		for condition, expression, should_retun_null in node.cases:
			condition_value = result.runtimeFilter(self.visit(condition, context)) # the expression which will be if the condition is true
			if result.should_return(): return result

			if condition_value.is_true():
				# Remember, when we found if, there may be elif, so we loop through them 
				expr_value = result.runtimeFilter(self.visit(expression, context)) # The context has variables, for local and global and expression to execute to get the value 
				if result.should_return(): return result
				return result.success(Number.null if should_retun_null else expr_value)

		# When we get the else, we return the value. The else node case is optional because
		# an expression might be ended with just elif. elif takes an expression by the way 
		if node.else_case:
			expression, should_retun_null = node.else_case
			else_value = result.runtimeFilter(self.visit(expression, context))
			if result.should_return(): return result
			return result.success(Number.null if should_retun_null else else_value)

		return result.success(Number.null)
	
	def visit_ForNode(self, node, context):

		result = RunTimeResult()

		elements = []

		# The start value such --> for i= 0
		start_value = result.runtimeFilter(self.visit(node.start_value_node, context))
		if result.should_return(): return result

		# The ending value after iteration
		end_value = result.runtimeFilter(self.visit(node.end_value_node, context))
		if result.should_return(): return result

		# increment or steps
		if node.step_value_node:
			step_value = result.runtimeFilter(self.visit(node.step_value_node, context))
			if result.should_return(): return result
		else:
			# If the step value is not introduced, we default it to one
			step_value = Number(1)

		i = start_value.value

		if step_value.value >= 0:
			condition = lambda: i < end_value.value # the return value is a boolean.  Lambda is an anonymous function
		else:
			condition = lambda: i > end_value.value
		
		# Iterating inside the loop
		while condition():
			context.symbol_table.set(node.var_name_tok.value, Number(i))
			i += step_value.value

			value = result.runtimeFilter(self.visit(node.body_node, context))
			if result.should_return() and result.loop_should_continue == False and result.loop_should_break == False: return result


			if result.loop_should_continue:
				continue

			if result.loop_should_break:
				break

			elements.append(value)


		return result.success(
			Number.null if node.should_return_null else 
			List(elements).setContext(context).setPosition(node.pos_start, node.pos_end
		))

	# The while loop
	def visit_WhileNode(self, node, context):
		result = RunTimeResult()

		elements = []

		while True: # as long the condition is true, you loop but usually there is a stop case to halt the loop
			condition = result.runtimeFilter(self.visit(node.condition_node, context))
			if result.should_return(): return result

			if not condition.is_true(): break

			value = result.runtimeFilter(self.visit(node.body_node, context))
			if result.should_return() and result.loop_should_continue == False and result.loop_should_break == False: return result

			if result.loop_should_continue:
				continue

			if result.loop_should_break:
				break

			elements.append(value)

		return result.success(
			Number.null if node.should_return_null else 
			List(elements).setContext(context).setPosition(node.pos_start, node.pos_end)
		)

	# visit the function definition
	def visit_FuncDefNode(self, node, context):
		res = RunTimeResult()

		func_name = node.var_name_tok.value if node.var_name_tok else None
		body_node = node.body_node
		arg_names = [arg_name.value for arg_name in node.arg_name_toks]

		# We retrieve the function value and its context
		func_value = Function(func_name, body_node, arg_names, node.should_auto_return).setContext(context).setPosition(node.pos_start, node.pos_end)
		
		if node.var_name_tok: # In case the function is not anonymous
			context.symbol_table.set(func_name, func_value)

		return res.success(func_value)

	# visit the call node
	def visit_CallNode(self, node, context):
		res = RunTimeResult()
		args = []
		 

		value_to_call = res.runtimeFilter(self.visit(node.node_to_call, context))
		if res.should_return(): return res

		value_to_call = value_to_call.copy().setPosition(node.pos_start, node.pos_end)

		for arg_node in node.arg_nodes:
			args.append(res.runtimeFilter(self.visit(arg_node, context)))
			if res.should_return(): return res

		# pdb.set_trace()

		body_node, new_context, should_auto_return = value_to_call.execute(args)

		if isinstance(body_node, RunTimeResult ):
			return res.success(body_node.value)

		ret_value = res.runtimeFilter(self.visit(body_node, new_context))
		if res.should_return() and res.func_return_value == None: return res

		# To check for the return value
		ret_value = (ret_value if should_auto_return else None) or res.func_return_value or Number.null
		
		# We update the context. the position and current varibles in the symbol
		return_value = ret_value.copy().setPosition(node.pos_start, node.pos_end).setContext(context)

		return res.success(return_value)

	def visit_ReturnNode(self, node, context):
		res = RunTimeResult()

		# If there is return value, we visit it and get it
		if node.node_to_return:
			value = res.runtimeFilter(self.visit(node.node_to_return, context))
			if res.should_return(): return res
		else:
			value = Number.null
		# We return it and the success return propagates the value up the tree
		return res.success_return(value)

	# They propagates the value that we should continue
	def visit_ContinueNode(self, node, context):
		return RunTimeResult().success_continue()

	# They propagates the value that we should continue
	def visit_BreakNode(self, node, context):
		return RunTimeResult().success_break()