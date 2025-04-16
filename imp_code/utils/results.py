#######################################
# RESULTS
#######################################

class RTResult:
	def __init__(self):
		self.value = None
		self.error = None
		self.should_break = False
		self.should_continue = False

	def register(self, res):
		if res.error: self.error = res.error
		return res.value

	def success(self, value):
		self.value = value
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


