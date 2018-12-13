# -*- coding: utf-8 -*-
import string
import re
import unicodedata
import collections
import bisect

from .const import (
    RUS_ALPHABET_STR,
    RUS_ALPHABET_SET,
    COMBINING_ACCENT_CHAR,
    COMBINING_BREVE_CHAR,
    COMBINING_DIURESIS_CHAR,
    EN_DASH_CHAR,
    HYPHEN_CHAR,
    RUS_PUNCT
)

RE_DIGITS_ONLY = re.compile(r'^\d+$')
RE_WHITESPACE_ONLY = re.compile(r'^\s+$')
TRANSLATOR_PUNCT_REMOVE = str.maketrans('', '', string.punctuation)

class Word(object):
    TYPE_UNDEFINED = 0
    TYPE_WORD = 1
    TYPE_HYPHENATED_WORD = 2
    TYPE_MWE = 3
    TYPE_NUMERIC = 4
    TYPE_WHITESPACE = 5
    TYPE_PUNCT = 6

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

    def gettext(self, remove_accents=False, remove_punct=False):
        '''
        Returns the word as a string.

        :param bool remove_accents: Remove acute accent marks
        :param bool remove_punct: Remove punctuation
        :param bool lowercase: Lowercase the string
        :param bool stripspace: Strip leading or trailing whitespace
        :return: the word string
        '''
        text = ''.join(self.tokens)
        if remove_accents:
            text = text.replace(COMBINING_ACCENT_CHAR, '')
        if remove_punct:
            text = text.translate(TRANSLATOR_PUNCT_REMOVE)
        return unicodedata.normalize('NFKC', text)

    def lower(self):
        return self.gettext().lower()

    def upper(self):
        return self.gettext().upper()

    def count(self):
        '''
        Number of tokens in the word.
        :return: number of tokens
        '''
        return len(self.tokens)

    def copy(self):
        '''
        Returns a copy of the word.
        :return: a new Word instance
        '''
        return Word(tokens=self.tokens.copy(), word_type=self.word_type)

    def is_russian(self):
        return self.word_type in (self.TYPE_WORD, self.TYPE_HYPHENATED_WORD, self.TYPE_MWE)

    def __eq__(self, other):
        return self.gettext() == other.gettext()

    def __lt__(self, other):
        return self.gettext() < other.gettext()

    def __le__(self, other):
        a, b = self.gettext(), other.gettext()
        return a == b or a < b

    def __repr__(self):
        return "Word(%s,%s)" % (self.tokens, self.word_type)

    def __str__(self):
        return self.gettext()


class WordList(object):
    def __init__(self, words):
        self.words = words

    def unique(self, case_sensitive=False):
        wordset = set()
        for w in self.words:
            if w.is_russian():
                wordstr = str(w)
                if not case_sensitive:
                    wordstr = wordstr.lower()
                wordset.add(wordstr)
        return list(sorted(wordset))

    def __repr__(self):
        return "WordList(%s)" % (self.words)

    def __str__(self):
        return str(self.words)

class WordTokenizer(object):
    def __init__(self, **kwargs):
        '''
        :param kwargs: Keyword args

        Keyword Args:
           case_sensitive (bool): Match case of MWEs (default False)
        '''
        self._mwes = []
        self._case_sensitive = kwargs.get('case_sensitive', False)

    def add_mwe(self, mwe):
        '''
        Adds a multi-word expression to the parser.

        :param str mwe: a multi word expression
        '''
        if not self._case_sensitive:
            mwe = mwe.lower()
        bisect.insort(self._mwes, mwe)

    def add_mwes(self, mwes):
        '''
        Adds a list of multi-word expressions.

        :param list mwe: a list of strings to treat as multi-word expressions
        '''
        for mwe in mwes:
            self.add_mwe(mwe)

    def tokenize(self, text):
        '''
        Parse the input text, returning a list of Word objects.

        :param str text: input text to parse
        :return: WordList object
        '''
        normalized_text = self._preprocess(text)
        tokens = self._tokenize(normalized_text)
        words = self._process(tokens)
        return WordList(words)

    def _preprocess(self, text):
        '''
        Preprocess the input text by normalizing hyphens and decomposing the unicode string is fully decomposed for
        easier parsing.

        :param str text: the input text
        :return: output text in NFKD form
        '''
        text = text.replace(EN_DASH_CHAR, HYPHEN_CHAR)
        nfkd_form = unicodedata.normalize('NFKD', text)
        return nfkd_form

    def _tokenize(self, text):
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
        pattern = "([0-9]+|[^0-9" + RUS_ALPHABET_STR + COMBINING_CHARS + "]+)"
        tokens = re.split(pattern, text)
        tokens = [t for t in tokens if t != '']
        return tokens

    def _process(self, tokens):
        '''
        Processes the tokens by converting them to word objects, classifying their type, and grouping
        hypheanted/multi-word expressions.

        :param list tokens: the list of tokens
        :return: list of Word objects
        '''
        tokenqueue = collections.deque(tokens)
        words = []
        while len(tokenqueue) > 0:
            token = tokenqueue.popleft()
            word = Word(token)
            if token[0] in RUS_ALPHABET_SET:
                word.word_type = Word.TYPE_WORD
                self._process_hyphenated(tokenqueue, word)
                self._process_mwes(tokenqueue, word)
            elif RE_WHITESPACE_ONLY.match(token):
                word.type = Word.TYPE_WHITESPACE
            elif RE_DIGITS_ONLY.match(token):
                word.type = Word.TYPE_NUMERIC
            elif all(p in token for p in RUS_PUNCT):
                word.type = Word.TYPE_PUNCT
            words.append(word)
        return words

    def _process_hyphenated(self, tokenqueue, word):
        '''
        Group hyphenated tokens together in the same word.

        :param tokenqueue: a queue of tokens
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

    def _process_mwes(self, tokenqueue, word):
        '''
        Group tokens that form the longest multi-word expression in the same word.

        Note: assumes sorted list of MWEs for binary search.
        Todo: a Trie data structure would be more efficient here.

        :param tokenqueue: a queue of tokens
        :param word: Word object to be augmented
        :return: True if MWE identified, False otherwise
        '''
        if len(self._mwes) == 0:
            return False
        w = word.copy()
        found_pos = found_index = -1
        pos = index = 0
        while index < len(tokenqueue):
            w.tokens.append(tokenqueue[index])
            expr = w.gettext(remove_accents=True)
            if not self._case_sensitive:
                expr = expr.lower()
            pos = bisect.bisect_left(self._mwes, expr, pos)
            if pos >= len(self._mwes) or len(expr) > len(self._mwes[pos]):
                break
            if self._mwes[pos] == expr:
                found_pos = pos
                found_index = index
            if self._mwes[pos].startswith(expr):
                index += 1
            else:
                break
        while found_index >= 0:
            word.tokens.append(tokenqueue.popleft())
            found_index -= 1
        return found_pos >= 0
