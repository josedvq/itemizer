import operator
from itemizer.alphabet import Alphabet

class ToRaw():
	""" Writes itemsets to file. """

	def __init__(self, filename, alphabet):
		""" Initializes attributes. """
		self.filename = filename
		self.alphabet = alphabet

	def __enter__(self):
		self.out_file = open(self.filename,"wb")
		return self

	def __exit__(self, exc_type, exc_value, exc_traceback):
		# TODO: manage exceptions
		self.out_file.close()

	def itemset(self, itemset):
		counts = [0 for i in range(0,len(self.alphabet))]
		for item in itemset:
			if item in self.alphabet:
				if counts[self.alphabet.translate_item(item)] < 255:
					counts[self.alphabet.translate_item(item)] += 1

		self.out_file.write(bytes(counts))
		if itemset.label is not None:
			self.out_file.write(bytes([itemset.label]))

	def end(self):
		return

	def print_meta(self, filename, separator=" ", translator=True):
		if translator:
			self.alphabet.translate()

		self.alphabet.print_to_file(filename,separator)
