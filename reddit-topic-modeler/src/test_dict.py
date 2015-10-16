class MyDict(dict):
	def __init__(self, *args):
		dict.__init__(self, args)
		self.defaults = {"a":1, "b":2}
	def __getitem__(self, key):
		val = dict.__getitem__(self, key)
		if isinstance(val, int) and val > -1:
			return val
		if (isinstance(val, str) or isinstance(val, list)) and len(val) > 0:
			return val
		try:
			self[key] = self.defaults[key]
			return self[key]
		except KeyError:
			raise KeyError("%s should not be a parameter.", val)

	def __setitem__(self, key, val):
		dict.__setitem__(self, key, val)

class MyOtherDict(dict):
	def __init__(self, **kwargs):
		dict.__init__(self, kwargs)

	def __getitem__(self, key):
		return dict.__getitem__(self, key)