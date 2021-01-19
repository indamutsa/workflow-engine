# This class shall filter error and keeps track of the result and successfully return the result
class RunTimeResult:
	def __init__(self):
		self.reset()

	
	def reset(self):
		self.value = None
		self.error = None
		self.func_return_value = None
		self.loop_should_continue = False # Propagate the node until we hit the for or while nodes
		self.loop_should_break = False

	def runtimeFilter(self, result):
		self.error = result.error
		self.func_return_value = result.func_return_value
		self.loop_should_continue = result.loop_should_continue
		self.loop_should_break = result.loop_should_break
		return result.value

	def success(self, value):
		self.reset()
		self.value = value
		return self

	def success_continue(self):
		self.reset()
		self.loop_should_continue = True
		return self

	def success_return(self, value):
		self.reset()
		self.func_return_value = value
		return self

	def success_break(self):
		self.reset()
		self.loop_should_break = True
		return self

	def failure(self, error):
		self.reset()
		self.error = error
		return self

	def should_return(self):
		# Note: this will allow you to continue and break outside the current function
		return (
			self.error or
			self.func_return_value or
			self.loop_should_continue or
			self.loop_should_break
		)

#  This class helps us keep tracl of the entry node and our current location in the tree
class Context:
    # For every node, it has the root error node where the error originated, the parent and itself
	def __init__(self, display_name, parent_node=None, root_err_node_pos=None):
		self.display_name = display_name
		self.parent_node = parent_node
		self.root_err_node_pos = root_err_node_pos
		self.symbol_table = None # This register our variables, function scope variables and the global variables that can be accessed anyway in the code