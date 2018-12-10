# -*- coding: utf-8 -*-
import string
import re
import unicodedata
import collections
import pygtrie

from pyrusbasic.const import (
    RUS_ALPHABET_STR,
    RUS_ALPHABET_SET,
    COMBINING_ACCENT_CHAR,
    COMBINING_BREVE_CHAR,
    COMBINING_DIURESIS_CHAR,
    EN_DASH_CHAR,
    HYPHEN_CHAR
)

RE_DIGITS_ONLY = re.compile(r'^\d+$')
RE_WHITESPACE_ONLY = re.compile(r'^\s+$')
TRANSLATOR_PUNCT_REMOVE = str.maketrans('', '', string.punctuation)

class Word(object):
    TYPE_UNDEFINED = 0
    TYPE_WORD = 1
    TYPE_HYPHENATED_WORD = 2
    TYPE_MWE = 3
    TYPE_WHITESPACE = 4
    TYPE_NUMERIC = 5

    def __init__(self, tokens=None, word_type:int = TYPE_UNDEFINED):
        '''
        :param list tokens: list of strings
        :param int word_type: word type indicator
        '''
        if tokens is None:
            self.tokens = []
        elif isinstance(tokens, str):
            self.tokens = [tokens]
        else:
            self.tokens = tokens
        self.word_type = word_type

    def gettext(self, remove_accents=False, remove_punct=False, lowercase=False, stripspace=False, normalize_unicode=True):
        '''
        Returns the word as a string.

        :param bool remove_accents: Remove acute accent marks
        :param bool remove_punct: Remove punctuation
        :param bool lowercase: Lowercase the string
        :param bool stripspace: Strip leading or trailing whitespace
        :param bool normalize_unicode: Normalize unicode characters in NFKC form, which yields the canonical composition
        :return: the word string
        '''
        text = ''.join(self.tokens)
        if remove_accents:
            text = text.replace(COMBINING_ACCENT_CHAR, '')
        if remove_punct:
            text = text.translate(TRANSLATOR_PUNCT_REMOVE)
        if lowercase:
            text = text.lower()
        if stripspace:
            text = text.strip()
        if normalize_unicode:
            text = unicodedata.normalize('NFKC', text)
        return text

    def canonical(self):
        '''
        Returns the canonical string representation of the word with the following characteristics:

        - Accent marks removed
        - Leading and trailing white space removed
        - Normalized unicode in NFKC form

        :return: the canonical string representation of the word
        '''
        return self.gettext(remove_accents=True, lowercase=True, stripspace=True, normalize_unicode=True)

    def numtokens(self):
        '''
        Number of tokens in the word.
        :return: number of tokens
        '''
        return len(self.tokens)

    def getdata(self):
        '''
        Returns a list representation of the word data, containing the word type followed by the raw tokens.
        :return: list of word data
        '''
        return [self.word_type] + self.tokens

    def copy(self):
        '''
        Returns a copy of the word.
        :return: a new Word instance
        '''
        return Word(tokens=self.tokens.copy(), word_type=self.word_type)

    def __repr__(self):
        return str(self.getdata())

    def __str__(self):
        return self.gettext()

class Preprocessor(object):
    def preprocess(self, text):
        '''
        Preprocess the input text by normalizing hyphens and decomposing the unicode string is fully decomposed for
        easier parsing.

        :param str text: the input text
        :return: output text in NFKD form
        '''
        text = text.replace(EN_DASH_CHAR, HYPHEN_CHAR)
        nfkd_form = unicodedata.normalize('NFKD', text)
        return nfkd_form

class Tokenizer(object):
    def tokenize(self, text):
        '''
        Returns a list of tokens (strings) that have been split into groups of russian characters (including accent
        marks), and groups of non-russian characters.

        Assumptions:
        - The input text has been fully decomposed (NFKD form)
        - Upper/lower case should be preserved
        - Punctuation/whitespace should be preserved

        :param str text: the input text
        :return: a list of tokens or strings
        '''
        COMBINING_CHARS = COMBINING_ACCENT_CHAR + COMBINING_BREVE_CHAR + COMBINING_DIURESIS_CHAR
        pattern = "([^" + RUS_ALPHABET_STR + COMBINING_CHARS + "]+)"
        tokens = re.split(pattern, text)
        tokens = [t for t in tokens if t != '']
        return tokens

class Parser(object):
    def __init__(self, **kwargs):
        '''
        :param kwargs: Keyword args

        Keyword Args:
           preprocessor (object): Object that implements a preprocess() method.
           tokenizer (object): Object that implements a tokenize() method.
           mwe_match_case (bool): Match case of MWEs (default False)
        '''
        self._mwes = pygtrie.Trie()
        self._preprocessor = kwargs.get('preprocessor', Preprocessor())
        self._tokenizer = kwargs.get('tokenizer', Tokenizer())
        self._mwe_match_case = kwargs.get('mwe_match_case', False)

    def add_mwe(self, mwe):
        '''
        Adds a multi-word expression to the parser.

        :param str mwe: a multi word expression
        '''
        if not self._mwe_match_case:
            mwe = mwe.lower()
        self._mwes[mwe] = True

    def add_mwes(self, mwes):
        '''
        Adds a list of multi-word expressions.

        :param list mwe: a list of strings to treat as multi-word expressions
        '''
        for mwe in mwes:
            self.add_mwe(mwe)

    def preprocess(self, text):
        '''
        Returns the preprocessed text.

        :param str text: input text
        :return: preprocessed text
        '''
        return self._preprocessor.preprocess(text)

    def tokenize(self, text):
        '''
        Returns tokens from the text.

        :param str text: input text
        :return: list of tokens
        '''
        return self._tokenizer.tokenize(text)

    def process_tokens(self, tokens):
        '''
        Processes the tokens by converting them to word objects, classifying their type, and grouping
        hypheanted/multi-word expressions.

        :param list tokens: the list of tokens
        :return: list of Word objects
        '''
        tokenqueue = collections.deque(tokens)
        words = []
        while len(tokenqueue) > 0:
            # Initialize word object with first token from the queue
            token = tokenqueue.popleft()
            word = Word(tokens=token)

            # Assume the word is russian if the first letter is russian based on the tokenization method
            if token[0] in RUS_ALPHABET_SET:
                word.word_type = Word.TYPE_WORD
                self.extract_hyphenated(tokenqueue, word)
                self.extract_mwe(tokenqueue, word)
            elif RE_WHITESPACE_ONLY.match(token):
                word.type = Word.TYPE_WHITESPACE
            elif RE_DIGITS_ONLY.match(token):
                word.type = Word.TYPE_NUMERIC

            words.append(word)
        return words

    def extract_hyphenated(self, tokenqueue, word):
        '''
        Lookahead in the token queue to see if the word is hyphenated, and if so, augment the word.

        :param tokenqueue: a deque of tokens
        :param word: Word object to be augmented
        :return: True if hyphenated word identified, False otherwise
        '''
        found_hyphen = len(tokenqueue) > 0 and tokenqueue[0] == HYPHEN_CHAR
        if found_hyphen:
            word.type = Word.TYPE_HYPHENATED_WORD
            word.tokens.append(tokenqueue.popleft())
            if len(tokenqueue) > 0 and tokenqueue[0][0] in RUS_ALPHABET_SET:
                word.tokens.append(tokenqueue.popleft())
        return found_hyphen

    def extract_mwe(self, tokenqueue, word):
        '''
        Lookahead in the token queue to see if the word is part of MWE, and if so, augment the word.

        :param tokenqueue: a deque of tokens
        :param word: Word object to be augmented
        :return: True if MWE identified, False otherwise
        '''
        w = word.copy()
        matched = False
        j = 0
        while j < len(tokenqueue):
            w.tokens.append(tokenqueue[j])
            expr = w.gettext(remove_accents=True, lowercase=not self._mwe_match_case)
            if self._mwes.has_subtrie(expr):
                j += 1
                matched = True
                continue
            elif self._mwes.has_key(expr):
                matched = True
                break
            else:
                j -= 1
                break
        if matched:
            while j >= 0:
                word.tokens.append(tokenqueue.popleft())
                j -= 1
        return matched

    def parse(self, text):
        '''
        Parse the input text, returning a list of Word objects.

        :param str text: input text to parse
        :return: list of Word objects
        '''
        nfkd_text = self.preprocess(text)
        tokens = self.tokenize(nfkd_text)
        words = self.process_tokens(tokens)
        return words
