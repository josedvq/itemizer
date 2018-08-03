import abc
import re
import copy

import requests
import itertools

from itemizer.element import TextElement, Itemset
from itemizer.dataset import TextDataset, ItemsetDataset

class Processor(abc.ABC):
    ''' Processes an element and returns the resulting lines. '''

    def __init__(self):
        super().__init__()

    @abc.abstractmethod
    def process(self, elem):
        pass


class ProcessorNormalize(Processor):
    ''' Processes strings into strings. Normalizes sentences using regular expressions to remove common dataset noise.'''

    cnt = 0

    def __init__(self, config):
        super().__init__()

        self._current = None

        def gutenbergNormalization(txt):
            valid_ending_chars = ['.', '"', '!', '-', '—',
                                  '?', '', '\'', '´', '’', ':', ')', ','],

            if txt[-1] not in valid_ending_chars and '.' not in txt and len(txt.split(' ')) < 15:
                return
            else:
                return txt

        # defaults
        self._config = {
            'logging': False,
            'name': 'ProcessorNormalize_' + str(ProcessorNormalize.cnt),
            'normalize_fn': gutenbergNormalization,
            # log the line if some of these chars is found, when logging is
            # enabled
            'log_char_regex': '[^ ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,:;\$\-—?()\'"!&=\/]',
            # lines ending in different chars are ignored

            # specific regexes
            'ignore_regex': [
                '^CHAPTER'
            ]
        }
        ProcessorNormalize.cnt += 1

        self._stats = {
            'in': {
                'cnt': 0
            },
            'out': {
                'cnt': 0
            }
        }

        self._config.update(config)

    def log_elem(self, elem):
        return False

    def process(self, elem):
        self._stats['in']['cnt'] += 1
        self._current = elem

        # create the new element to work on
        elem = copy.copy(elem)

        # apply custom normalization function
        if self._config['normalize_fn']:
            elem.string = self._config['normalize_fn'](elem.string)
        if not elem.string:
            return self.log_elem(elem)

        # generally applicable filtering
        # ignore string with no lower caps
        if not re.search('[a-z]', elem.string):
            return self.log_elem(elem)
        # ignore footnotes
        if re.match('^\s*\[[0-9]+\]', elem.string):
            return self.log_elem(elem)
        if re.match('^\s*\{[0-9]+\}', elem.string):
            return self.log_elem(elem)
        # ignore lines starting with parentheses / braces
        if re.match('^\s*\[', elem.string):
            return self.log_elem(elem)
        if re.match('^\s*\{', elem.string):
            return self.log_elem(elem)
        if re.match('^\s*\(', elem.string):
            return self.log_elem(elem)
        # ignore lines ending with unmatched parentheses / braces
        if re.match('^[^\[]+\]$', elem.string):
            return self.log_elem(elem)
        if re.match('^[^\{]+\}$', elem.string):
            return self.log_elem(elem)
        if re.match('^[^\(]+\)$', elem.string):
            return self.log_elem(elem)
        # ignore indented text
        if elem.string[0] == ' ':
            return self.log_elem(elem)
        # ignore lines containing tabs
        if re.search('[\t]', elem.string):
            return self.log_elem(elem)

        # generally applicable filtering
        elem.string = re.sub('\*', '', elem.string)
        # replace more than 4 consecutive dots by 4 dots
        elem.string = re.sub('\. \. \.(:? \.)+', '....', elem.string)
        elem.string = re.sub('\.\.\.(:?\.)+', '....', elem.string)
        # join triple dots
        elem.string = re.sub('\. \. \.', '...', elem.string)
        # join double dots
        elem.string = re.sub('\. \.', '..', elem.string)
        # remove square brackets
        elem.string = re.sub('\[([^\]]*)\]', '', elem.string)
        # remove braces
        elem.string = re.sub('\{[^}]*\}', '', elem.string)
        # remove underscores
        elem.string = re.sub('_', '', elem.string)
        # replace other dashes by normal dashes
        elem.string = re.sub('[–−]', '-', elem.string)
        # replace double dashes by em-dashes
        elem.string = re.sub('--', '—', elem.string)
        # replace other quotation marks
        elem.string = re.sub('[”“]', '"', elem.string)
        elem.string = re.sub('[`´‘’]', '\'', elem.string)
        # replace more than 2 em-dashes by 2 em-dashes
        elem.string = re.sub('[—]{3,}', '——', elem.string)
        # colapse multiple spaces
        elem.string = re.sub(' +', ' ', elem.string)
        # remove trailing whitespace
        elem.string = elem.string.strip()

        if elem.string == '':
            return self.log_elem(elem)
        else:
            return elem

    def process_dataset(self,dataset):
        assert isinstance(dataset,TextDataset)

        new_dataset = TextDataset()
        for line in dataset:
            new_line = self.process(line)
            if new_line:
                new_dataset.append(new_line)

        return new_dataset


class ProcessorTokenize(Processor):
    ''' Processes strings into itemsets. Converts a text into itemsets/tokens by splitting and possibly lemmatizing the tokens '''

    cnt = 0

    def __init__(self, config):
        super().__init__()

        self._current = None

        # defaults
        self._config = {
            'logging': False,
            'name': 'ProcessorTokenize_' + str(ProcessorNormalize.cnt),
            'lemmatize': False,
            'sentence_split': False,
            'min_length': 0,
            'parentheses_action': 'delete',
            'pos_filter': None,
            'stop_words': None,
            'split_on': [],
            'stop_words': False,
            'core_nlp_api_uri': 'http://localhost:9000/'
        }

        # merge config options
        self._config.update(config)

        # processing config
        if self._config['pos_filter']:
            if self._config['pos_filter'][0] == '^':
                self._config['pos_filter_negative'] = True
                self._config['pos_filter'] = self._config['pos_filter'][1:].split('|')
            else:
                self._config['pos_filter'] = self._config['pos_filter'].split('|')
        else:
            # default: allow all
            self._config['pos_filter_negative'] = True
            self._config['pos_filter'] = []

        if self._config['pos_to_substitute']:
            self._config['pos_to_substitute'] = self._config['pos_to_substitute'].split('|')
        else:
            self._config['pos_to_substitute'] = []

        self._stop_words = []
        self._stop_regexes = []
        if self._config['stop_words']:
            for stop_word in self._config['stop_words']:
                m = re.match('^rgx:(.*)', stop_word)
                if m:
                    self._stop_regexes.append(m.group(1))
                else:
                    self._stop_words.append(stop_word)

        self._stats = {
            'in': {
                'chunks': 0,
                'sentences': 0,
                'tokens': 0,
                'tokens_outside_quotes': 0
            },
            'out': {
                'itemsets': 0,
                'items': 0
            }
        }

        ProcessorTokenize.cnt += 1

    def _is_stop_word(self, word):
        if word in self._stop_words:
            return True

        for regex in self._stop_regexes:
            if re.match(regex, word):
                return True

        return False

    def log_elem(self, elem):
        return False

    def process(self, elem):

        self._stats['in']['chunks'] += 1
        self._current = copy.copy(elem)

        itemsets = []
        itemset = Itemset()
        itemset.label = elem.label

        # prepare request to CoreNLP
        annotators = "tokenize,ssplit,pos"
        if self._config['lemmatize']:
            annotators = "lemma," + annotators

        response = requests.post('{core_nlp_api_uri}?properties={{"annotators":"{annotators}","outputFormat":"json"}}'.format(
            core_nlp_api_uri=self._config['core_nlp_api_uri'], annotators=annotators), data=elem.string.encode('utf-8'))

        # if there is an error
        response.raise_for_status()
        json = response.json()

        # PROCESSING STARTS
        previous_char_offset = 0
        quotes_open = False
        words = []
        txt = ''

        for i, sentence in enumerate(json['sentences']):
            self._stats['in']['sentences'] += 1

            for j, token in enumerate(sentence['tokens']):
                self._stats['in']['tokens'] += 1

                original_text = token['originalText']
                do_add = True

                if original_text == '"':
                    if i+j > 0:
                        quotes_open = not quotes_open
                    else:
                        quotes_open = True

                else:
                    # possibly ignore words between quotes
                    if quotes_open and self._config['parentheses_action'] == 'delete':
                        continue

                # filter by POS
                if self._config['pos_filter_negative']:
                    if token['pos'] in self._config['pos_filter']:
                        do_add = False
                else:
                    if token['pos'] not in self._config['pos_filter']:
                        do_add = False

                # get lemma or lowercase word
                word = None
                if quotes_open and original_text != '"' and self._config['parentheses_action'] == 'substitute':
                    word = '<QQQ>'
                elif self._config['lemmatize']:
                    word = token['lemma']
                else:
                    word = token['word'].lower()

                # ignore stopwords
                if self._config['stop_words'] and self._is_stop_word(word):
                    do_add = False

                # substitute POSes
                if token['pos'] in self._config['pos_to_substitute']:
                    word = '<{pos}>'.format(pos=token['pos'])

                # ignore closing
                if word == "''":
                    do_add = False

                # add the word
                if do_add:
                    itemset.append(word)

                previous_char_offset = token['characterOffsetEnd']

                # split on
                if not quotes_open and (original_text in self._config['split_on'] or (self._config['sentence_split'] and j == len(sentence['tokens'])-1)):
                    if len(itemset) > self._config['min_length']:
                        itemsets.append(itemset)
                        itemset = Itemset()
                        itemset.label = elem.label

            if len(itemset) > self._config['min_length']:
                itemsets.append(itemset)
                itemset = Itemset()
                itemset.label = elem.label

        return itemsets

    def process_dataset(self,dataset):
        assert isinstance(dataset,TextDataset)

        new_dataset = ItemsetDataset()
        for line in dataset:
            output_lines = self.process(line)
            for line in output_lines:
                new_dataset.append(line)

        return new_dataset
