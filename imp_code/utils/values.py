#######################################
# VALUES
#######################################

from imp_code.components.errors import *

class Value:
	def __init__(self, value):
		self.value = value
		self.set_pos()
		self.set_context()

	def set_pos(self, pos_start=None, pos_end=None):
		self.pos_start = pos_start
		self.pos_end = pos_end
		return self

	def set_context(self, context=None):
		self.context = context
		return self

	def added_to(self, other):
		if isinstance(other, Value):
			return Value(self.value + other.value).set_context(self.context), None

	def subbed_by(self, other):
		if isinstance(other, Value):
			return Value(self.value - other.value).set_context(self.context), None

	def multed_by(self, other):
		if isinstance(other, Value):
			return Value(self.value * other.value).set_context(self.context), None

	def dived_by(self, other):
		if isinstance(other, Value):
			if other.value == 0:
				return None, RTError(
					other.pos_start, other.pos_end,
					'Division by zero',
					self.context
				)

			return Value(self.value / other.value).set_context(self.context), None
		
	def remained_by(self, other):
		if isinstance(other, Value):
			if other.value == 0:
				return None, RTError(
					other.pos_start, other.pos_end,
					'Modulo by zero',
					self.context
				)

			return Value(self.value % other.value).set_context(self.context), None

	def __repr__(self):
		return str(self.value)
