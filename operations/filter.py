import operator

from itemizer.alphabet import Alphabet
from itemizer.element import Itemset

class Filter():
	""" Filters an itemset file. """

	def __init__(self, alphabet=None, translate=False):
		""" Initializes attributes. """
		self.alphabet = alphabet
		self.new_alphabet = Alphabet()
		self.translate = translate
		self.connected_pipes = []

	def itemset(self, itemset):
		new_itemset = Itemset(separator=itemset.separator,label=itemset.label)

		assert (self.alphabet is not None), "Alphabet not set."

		for item in itemset:
			if item in self.alphabet:
				if self.translate:
					translated_item = self.alphabet.translate_item(item)
					self.new_alphabet[translated_item] += 1
					new_itemset.append(translated_item)
				else:
					self.new_alphabet[item] += 1
					new_itemset.append(item)

		if new_itemset:
			for pipe in self.connected_pipes:
				pipe.itemset(new_itemset)

	def end(self):
		for pipe in self.connected_pipes:
			pipe.end()
		return

	def pipe(self, operation_obj):
		self.connected_pipes.append(operation_obj)

	def print_meta(self, filename, separator=" ", translator=True):
		if translator:
			self.alphabet.translate()

		self.alphabet.print_to_file(filename,separator)
