from app.utils.error_display import *


class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start # This position help us keep track of where the error originated
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def tracebackError(self):
        # pdb.set_trace()
        result = f'{self.error_name} : {self.details}\n'
        result += f'File: {self.pos_start.filename}, Line number: {self.pos_start.line_num + 1}'
        result += '\n\n' + error_pointer(self.pos_start.file_text, self.pos_start, self.pos_end)
        return result

class IllegalCharacter(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__( pos_start, pos_end, 'Illegal Character', details)


class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'Invalid Syntax', details)

# The runtime error: this class we trace back the tree with the error provided
class RunTimeError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, 'Runtime Error: ', details)
        self.context = context

    # This method traces back the error
    def tracebackError(self):

        result  = self.generate_traceback()
        result += f'{self.error_name}: {self.details}'
        result += '\n\n' + error_pointer(self.pos_start.file_text, self.pos_start, self.pos_end)
        return result

    def generate_traceback(self):
        result = ''
        pos = self.pos_start
        context = self.context

        # while the context is not null, we will go up 
        while context:
            result = f'File: {pos.filename}, line number: {str(pos.line_num + 1)}, in {context.display_name}\n' + result
            pos = context.root_err_node_pos
            context = context.parent_node

        return 'Error from :\n' + result

class ExpectedCharError(Error):
	def __init__(self, pos_start, pos_end, details):
		super().__init__(pos_start, pos_end, 'Expected Character', details)