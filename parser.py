from itemizer.element import Itemset

class Parser():
	def __init__(self, separator=" "):
		self.connected_pipes = []
		self.separator = separator

	def parse_line(self, line):
		itemset = Itemset(separator = self.separator).from_string(line)

		for pipe in self.connected_pipes:
			pipe.itemset(itemset)

	def parse_file(self, filename):
		with open(filename) as fin:
			for line in fin:
				self.parse_line(line[:-1])
		for pipe in self.connected_pipes:
			pipe.end()

	def pipe(self, operation_obj):
		self.connected_pipes.append(operation_obj)
