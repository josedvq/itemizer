import operator
from itemizer.alphabet import Alphabet

class ToCsv():
	""" Writes itemsets to file. """

	def __init__(self, filename, alphabet):
		""" Initializes attributes. """
		self.filename = filename
		self.alphabet = alphabet
		self.separator = " "

	def __enter__(self):
		self.out_file = open(self.filename,"w")
		return self

	def __exit__(self, exc_type, exc_value, exc_traceback):
		# TODO: manage exceptions
		self.out_file.close()

	def itemset(self, itemset):
		counts = [0 for i in range(0,len(self.alphabet))]
		for item in itemset:
			counts[self.alphabet.translate_item(item)] += 1

		self.out_file.write(self.separator.join(map(str,counts)))
		if itemset.cls is not None:
			self.out_file.write(" "+str(itemset.cls))
		self.out_file.write("\n")

	def end(self):
		return

	def print_meta(self, filename, separator=" ", translator=True):
		if translator:
			self.alphabet.translate()

		self.alphabet.print_to_file(filename,separator)