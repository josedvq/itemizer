import re


class Alphabet():

    def __init__(self):
        self.counts = dict()
        self.alphabet = []
        self.translator = dict()

        # Iteration
        self.current = -1

    def __contains__(self, key):
        return key in self.counts

    def __getitem__(self, key):
        # implement a default of 0
        if not key in self.counts:
            return 0
        return self.counts[key]

    def __setitem__(self, key, item):
        self.counts[key] = item

    def __str__(self):
        return self.to_string(" ")

    def __len__(self):
        return len(self.alphabet)

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= len(self.alphabet)-1:
            raise StopIteration
        else:
            self.current += 1
        return self.alphabet[self.current]

    next = __next__

    def append(self, item, count = 0):
        self.alphabet.append(item)
        self.counts[item] = count

    def reset_counts(self):
        for key in self.counts:
            self.counts[key] = 0

    def translate(self, first_item=0):
        sorted_alphabet = sorted(
            self.counts.items(), key=lambda kv: kv[1], reverse=True)
        self.alphabet = [e[0] for e in sorted_alphabet]
        self.translator = {key: (idx + first_item) for idx, key in enumerate(self.alphabet)}

    def translate_item(self, item):
        return self.translator[item]

    def keep_n(self, n):
        self.alphabet = self.alphabet[:n]

        new_counts = dict()
        for word in self.alphabet:
            new_counts[word] = self.counts[word]

        self.counts = new_counts
        self.translator = {key: idx for idx, key in enumerate(self.alphabet)}

    def keep_min_frequency(self, f):
        self.alphabet = [e for e in self.alphabet if self.counts[e] >= f]

        new_counts = dict()
        for word in self.alphabet:
            new_counts[word] = self.counts[word]

        self.counts = new_counts
        self.translator = {key: idx for idx, key in enumerate(self.alphabet)}

    def intersect(self, alphabet, counts='keep'):
        '''Intersect with another alphabet and return the resulting alphabet'''
        intersection = Alphabet()

        for item in self:
            if item in alphabet:
                count = None
                if counts == 'keep':
                    count = self.counts[item]
                elif counts == 'take':
                    count = alphabet.counts[item]
                elif counts == 'add':
                    count = self.counts[item] + alphabet.counts[item]
                else:
                    raise ValueError('Unknown value for arg counts.')

                intersection.append(item,count)
        intersection.translate()
        return intersection

    def to_string(self, separator=" "):
        out_str = "SI:" + str(len(self)) + "\n"

        # write alphabet
        out_str += ("AB:" + separator +
                    separator.join(map(str, self.counts.keys())) + "\n")

        # write counts
        out_str += ("CT:" + separator +
                    separator.join(map(str, self.counts.values())) + "\n")

        # write translator
        if self.alphabet:
            out_str += ("IT:" + separator +
                        separator.join(list(self.alphabet)) + "\n")

        return out_str

    def to_file(self, filename, separator=" "):
        with open(filename, "w") as fout:
            fout.write(self.to_string(separator))


    def from_file(self, filename, separator=" "):
        alphabet = []
        counts = []
        translator = []

        with open(filename) as fin:
            for line in fin:
                # read alphabet
                if re.match("^AB:.*", line):
                    alphabet = line[4:-1].split(separator)

                if re.match("^CT:.*", line):
                    counts = list(map(int, line[4:-1].split(separator)))

                if re.match("^IT:.*", line):
                    translator = line[4:-1].split(separator)

        assert alphabet, "Alphabet not present in file."
        assert counts, "Counts not present in file."

        assert (len(alphabet) == len(counts)
                ), "Alphabet and Counts do not have the same length."
        if translator:
            assert (len(translator) == len(alphabet)
                    ), "Translator length is different from Alphabet's length."

        self.counts = dict(zip(alphabet, counts))
        self.alphabet = translator
        if translator:
            self.translator = {key: idx for idx, key in enumerate(self.alphabet)}

        return self
