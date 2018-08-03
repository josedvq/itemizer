import re
import abc

class Element(abc.ABC):
    ''' Represents an element(row) of a dataset '''

    def __init__(self):
        # class of the element
        self.label = None

    @abc.abstractmethod
    def __str__(self):
        pass

    @abc.abstractmethod
    def to_string(self):
        pass

    @abc.abstractmethod
    def from_string(self):
        pass

class Itemset(Element):
    """ A single itemset element """

    def __init__(self, items=None, label=None, separator=" "):
        super().__init__()
        self.items = items
        if items is None:
            self.items = []
        self.label = label
        self.separator = separator

    def __str__(self):
        return self.to_string()

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        self.current = -1
        return self

    def __next__(self):
        if self.current >= len(self.items)-1:
            raise StopIteration
        else:
            self.current += 1
            return self.items[self.current]

    def append(self, item):
        self.items.append(item)

    # Removes the first occurrence of item
    def remove(self,item):
        self.items.remove(item)

    def to_string(self, add_class=True):
        string = self.separator.join(map(str,self.items))
        if self.label is not None and add_class:
            string += " ["+str(self.label)+"]"

        return string

    def from_string(self, string, separator=" "):
        self.separator = separator

        parts = string.split(separator)
        match_obj = re.match("^\[([^\[\]]+)\]$", parts[-1])

        if match_obj:
            self.label = int(match_obj.group(1))
            del parts[-1]

        self.items = parts

        return self

class TextElement(Element):
    """ A simple text """

    def __init__(self, string=None, label=None):
        super().__init__()

        self.string = string
        self.label = label

    def __str__(self):
        return self.to_string()

    def append(self,string):
        if not self.string: self.string = string
        else: self.string += string

    def to_string(self, add_class=True):
        if add_class and self.label is not None:
            return self.string + ' [' + str(self.label) + ']'
        else:
            return self.string

    def from_string(self, string):
        match_obj = re.match("^(.*)\[([^\[\]]+)\]$", string)

        if match_obj:
            self.string = match_obj.group(1)
            self.label = int(match_obj.group(2))
        else:
            self.string = string
            self.label = None

        return self
