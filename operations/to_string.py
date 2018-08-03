import operator
from itemizer.alphabet import Alphabet

class ToString():
	""" Writes itemsets to file. """

	def __init__(self, filename, add_class=False):
		""" Initializes attributes. """
		self.filename = filename
		self.add_class = add_class

	def __enter__(self):
		self.out_file = open(self.filename,"w")
		return self

	def __exit__(self, exc_type, exc_value, exc_traceback):
		# TODO: manage exceptions
		self.out_file.close()

	def itemset(self, itemset):
		out_string = itemset.to_string(add_class=False)
		if self.add_class:
			out_string += " "+str(itemset.cls)
		out_string += "\n"
		self.out_file.write(out_string)

	def end(self):
		return

	def print_meta(self, filename, separator=" ", translator=True):
		if translator:
			self.alphabet.translate()

		self.alphabet.print_to_file(filename,separator)