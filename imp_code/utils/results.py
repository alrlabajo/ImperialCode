#######################################
# RESULTS
#######################################

class RTResult:
	def __init__(self):
		self.value = None
		self.error = None
		self.should_break = False
		self.should_continue = False
		self.return_value = None

	def register(self, res):
		if res.error: self.error = res.error
		if hasattr(res, 'return_value') and res.return_value is not None:
			self.return_value = res.return_value
		return res.value

	def success(self, value):
		self.value = value
		return self
	
	def success_return(self, value):
		self.return_value = value
		self.return_value = value
		return self

	def failure(self, error):
		self.error = error
		return self

	def should_break_execution(self):
		self.should_break = True
		return self

	def should_continue_execution(self):
		self.should_continue = True
		return self


