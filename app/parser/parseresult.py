# In case there is an error in the parsed result, this class will generate the error
class ParseFilter:
	def __init__(self):
		self.error = None
		self.node = None
		self.increment_count = 0
		self.last_registered_increment_count = 0
		self.to_reverse_count = 0

	def filterError(self, res):
        # We check if the parsed result is of ExceptionFilter type and if it has an error
		self.last_registered_increment_count = res.increment_count
		self.increment_count += res.increment_count
		if res.error: self.error = res.error

		 # If no error, we bring back the parsed node from the Parser Class
		return res.node

	def registerStatement(self, res):
		if res.error:
			self.to_reverse_count = res.increment_count
			return None # If it fails
		return self.filterError(res)

	# This function helps figure the error expected var... such as
	# 6 + var a = 5
	#	   ^
	#      Expected int, float, ...	
	# We can only override this message, when there was no advancement
	def register_advancement(self):
		self.increment_count += 1

    # This will return the node (which is essentially a tree) because the node might have children
	def success(self, node):
		self.node = node
		return self

    # This will assign the error

	# This function helps figure the error (Expected var...) such as
	# 6 + var a = 5
	#	   ^
	#      (Expected int, float, ...)	
	# We can only override this message, when there was no advancement
	def failure(self, error):
		if not self.error or self.increment_count == 0:
			self.error = error
		return self