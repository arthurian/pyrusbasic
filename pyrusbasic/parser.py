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

RE_WHITESPACE_ONLY = re.compile(r'^\s+$')
TRANSLATOR_PUNCT_REMOVE = str.maketrans('', '', string.punctuation)

class Word(object):
    TYPE_WORD = 1
    TYPE_HYPHENATED_WORD = 2
    TYPE_MWE = 3
    TYPE_WHITESPACE = 4
    TYPE_OTHER = 5

    def __init__(self, tokens=None, word_type=None):
        if tokens is None:
            self.tokens = []
        elif isinstance(tokens, str):
            self.tokens = [tokens]
        else:
            self.tokens = tokens
        self.word_type = word_type

    def gettext(self, remove_accents=False, remove_punct=False, lowercase=False):
        text = ''.join(self.tokens)
        if remove_accents:
            text = text.replace(COMBINING_ACCENT_CHAR, '')
        if remove_punct:
            text = text.translate(TRANSLATOR_PUNCT_REMOVE)
        if lowercase:
            text = text.lower()
        return text

    def canonical(self):
        return self.gettext(remove_accents=True)

    def numtokens(self):
        return len(self.tokens)

    def getdata(self):
        return [self.word_type] + self.tokens

    def copy(self):
        return Word(tokens=self.tokens.copy(), word_type=self.word_type)

    def __repr__(self):
        return str(self.getdata())

    def __str__(self):
        return self.gettext()

class Preprocessor(object):
    def preprocess(self, text):
        text = text.replace(EN_DASH_CHAR, HYPHEN_CHAR)
        nfkd_form = unicodedata.normalize('NFKD', text)
        return nfkd_form

class Tokenizer(object):
    def tokenize(self, text):
        # First pass at splitting text into groups of russian characters, including accents, and then all others.
        # Assumes normalized in NFKD form.
        # Note the intention is to preserve upper/lower case characters and all whitespace, punctuation, etc
        COMBINING_CHARS = COMBINING_ACCENT_CHAR + COMBINING_BREVE_CHAR + COMBINING_DIURESIS_CHAR
        pattern = "([^" + RUS_ALPHABET_STR + COMBINING_CHARS + "]+)"
        tokens = re.split(pattern, text)
        tokens = [t for t in tokens if t != '']
        return tokens

class Parser(object):
    def __init__(self, **kwargs):
        self._mwes = pygtrie.Trie()
        self.match_case = kwargs.get('match_case', False)

    def add_mwe(self, mwe):
        if not self.match_case:
            mwe = mwe.lower()
        self._mwes[mwe] = True

    def add_mwes(self, mwes):
        for mwe in mwes:
            self.add_mwe(mwe)

    def preprocess(self, text):
        return Preprocessor().preprocess(text)

    def tokenize(self, text):
        return Tokenizer().tokenize(text)

    def tokens2words(self, tokens):
        tokenqueue = collections.deque(tokens)
        words = []
        while len(tokenqueue) > 0:
            # Initialize word object with first token from the queue
            token = tokenqueue.popleft()
            word = Word(tokens=token)

            # Assume the word is russian if the first letter is russian based on the tokenization method
            if token[0] in RUS_ALPHABET_SET:
                word.word_type = Word.TYPE_WORD
                # Look ahead for hyphenated words or multi-word expressions
                if len(tokenqueue) > 0:
                    if tokenqueue[0] == HYPHEN_CHAR:
                        word.type = Word.TYPE_HYPHENATED_WORD
                        word.tokens.append(tokenqueue.popleft())
                        if tokenqueue[0][0] in RUS_ALPHABET_SET:
                            word.tokens.append(tokenqueue.popleft())
                    else:
                        self.find_mwe(tokenqueue, word)
            elif RE_WHITESPACE_ONLY.match(token):
                word.type = Word.TYPE_WHITESPACE

            words.append(word)
        return words

    def find_mwe(self, tokenqueue, word):
        w = word.copy()
        matched = False
        j = 0
        while j < len(tokenqueue):
            w.tokens.append(tokenqueue[j])
            expr = w.gettext(remove_accents=True, lowercase=not self.match_case)
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
        nfkd_text = self.preprocess(text)
        tokens = self.tokenize(nfkd_text)
        words = self.tokens2words(tokens)
        return words
