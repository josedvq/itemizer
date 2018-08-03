import random
import abc
import numpy as np

from itemizer.element import Itemset, TextElement
from itemizer.alphabet import Alphabet


class Dataset(abc.ABC):
    ''' abstract dataset class '''

    def __init__(self, filename=None):
        self._elements = []

        # iteration
        if filename is not None:
            self.from_file(filename)

    def __getitem__(self, idx):
        return self._elements[idx]

    def __setitem__(self, idx, elem):
        self._elements[idx] = elem

    def __iter__(self):
        self.current = -1
        return self

    def __len__(self):
        return len(self._elements)

    def __next__(self):
        if self.current >= len(self._elements) - 1:
            raise StopIteration
        else:
            self.current += 1
            return self._elements[self.current]

    def append(self, elem):
        self._elements.append(elem)

    def force_label(self, label):
        for elem in self._elements:
            elem.label = label

    def cv_split(self, folds):
        pass

    def shuffle(self, rndm):
        rndm.shuffle(self._elements)

    @abc.abstractmethod
    def to_file(self, filename):
        pass

    @abc.abstractmethod
    def from_file(self, filename):
        pass


class ItemsetDataset(Dataset):
    ''' Itemset dataset. Every item is a set of items from an alphabet. '''

    def __init__(self, filename=None, separator=' '):
        self.separator = separator
        super().__init__(filename)
        self.alphabet = None

        if filename is not None:
            self.compute_alphabet()

    def compute_alphabet(self):
        self.alphabet = Alphabet()
        for itemset in self:
            for item in itemset:
                self.alphabet[item] += 1

    def translate(self):
        translated_dataset = Dataset(separator=self.separator)
        translated_dataset.itemsets = []
        for itemset in self:
            translated_itemset = Itemset(
                items=None, cls=itemset.cls, separator=self.separator)
            for item in itemset:
                translated_itemset.append(self.alphabet.translate_item(item))
            translated_dataset.itemsets.append(translated_itemset)
        return translated_dataset

    def from_file(self, filename):
        with open(filename) as fin:
            for line in fin:
                self._elements.append(Itemset().from_string(
                    line, separator=self.separator))

    def to_file(self, filename, append=False):
        write_mode = 'w'
        if append:
            write_mode = 'a'
        with open(filename, write_mode) as fout:
            for itemset in self._elements:
                fout.write(str(itemset) + "\n")

    def to_raw(self, filename, alphabet=None, append=False):
        if alphabet:
            ab = alphabet
        else:
            ab = self.alphabet

        with open(filename, 'w') as fout:
            for itemset in self:
                counts = [0 for i in range(0, len(ab))]
                for item in itemset:
                    if item in ab:
                        if counts[ab.translate_item(item)] < 255:
                            counts[ab.translate_item(item)] += 1

                fout.write(bytes(counts))
                if itemset.label is not None:
                    fout.write(bytes([itemset.label]))

    def get_nparray(self, alphabet=None):
        print('HERe')
        print(len(self))
        if alphabet:
            ab = alphabet
        else:
            if not self.alphabet:
                raise ValueError(
                    'Attempting to get np array without an alphabet.')
            ab = self.alphabet

        arr = np.zeros(shape=(len(self), len(ab)), dtype=np.uint8)

        print('begin')
        for i, itemset in enumerate(self):
            for item in itemset:
                if item in ab:
                    if arr[i, ab.translate_item(item)] < 255:
                        arr[i, ab.translate_item(item)] += 1
        return arr


class TextDataset(Dataset):
    ''' Dataset where every element is simply a line of text. '''

    def __init__(self, filename=None):
        super().__init__(filename)
        self.alphabet = None

    def from_file(self, filename):
        with open(filename) as fin:
            for line in fin:
                self._elements.append(TextElement().from_string(line))

    def to_file(self, filename, append=False):
        write_mode = 'w'
        if append:
            write_mode = 'a'
        with open(filename, write_mode) as fout:
            for element in self._elements:
                fout.write(str(element) + "\n")

    def process(self, processor):
        return processor.process_dataset(self)

    def join_lines(self, separator=' '):
        new_element = TextElement()
        element_strings = []
        for element in self._elements:
            element_strings.append(element.string)
        new_element.string = separator.join(element_strings)
        if self._elements[0].label is not None:
            new_element.label = self._elements[0].label
        self._elements = [new_element]
        return self


class FeatureDataset(Dataset):
    ''' Dataset of features, where each column represents a particular feature.'''
    pass
