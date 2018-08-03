import operator
from itemizer.alphabet import Alphabet

class AlphabetExtractor():
	""" Extracts the alphabet from a file. """

	def __init__(self):
		""" Initializes attributes. """
		self.alphabet = Alphabet()

	def itemset(self, itemset):
		for item in itemset:
			self.alphabet[item] = self.alphabet[item]+1

	def end(self):
		return

	def print_meta(self, filename, separator=" ", translator=True):
		if translator:
			self.alphabet.translate()

		self.alphabet.to_file(filename,separator)
