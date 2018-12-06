# -*- coding: utf-8 -*-
import string
import re
import unicodedata
import collections
import pygtrie

RUS_ALPHABET_LIST = [
    '\u0410', '\u0430', # Аа
    '\u0411', '\u0431', # Бб
    '\u0412', '\u0432', # Вв
    '\u0413', '\u0433', # Гг
    '\u0414', '\u0434', # Дд
    '\u0415', '\u0435', # Ее
    '\u0401', '\u0451', # Ёё
    '\u0416', '\u0436', # Жж
    '\u0417', '\u0437', # Зз
    '\u0418', '\u0438', # Ии
    '\u0419', '\u0439', # Йй
    '\u041A', '\u043A', # Кк
    '\u041B', '\u043B', # Лл
    '\u041C', '\u043C', # Мм
    '\u041D', '\u043D', # Нн
    '\u041E', '\u043E', # Оо
    '\u041F', '\u043F', # Пп
    '\u0420', '\u0440', # Рр
    '\u0421', '\u0441', # Сс
    '\u0422', '\u0442', # Тт
    '\u0423', '\u0443', # Уу
    '\u0424', '\u0444', # Фф
    '\u0425', '\u0445', # Хх
    '\u0426', '\u0446', # Цц
    '\u0427', '\u0447', # Чч
    '\u0428', '\u0448', # Шш
    '\u0429', '\u0449', # Щщ
    '\u042A', '\u044A', # Ъъ
    '\u042B', '\u044B', # Ыы
    '\u042C', '\u044C', # Ьь
    '\u042D', '\u044D', # Ээ
    '\u042E', '\u044E', # Юю
    '\u042F', '\u044F', # Яя
]
RUS_ALPHABET_SET = set(RUS_ALPHABET_LIST)
RUS_ALPHABET_STR = "".join(RUS_ALPHABET_LIST)

COMBINING_ACCENT_CHAR = '\u0301' # E.g. for stress marks
COMBINING_BREVE_CHAR = '\u0306' # E.g. for eleventh letter in Russian alphabet, short i
COMBINING_DIURESIS_CHAR = '\u0308' # E.g. cyrillic e with diuresis

EN_DASH_CHAR = '\u2013'
HYPHEN_CHAR = '\u002D'

MULTI_WORD_EXPRESSIONS = [
    'потому, что',
    ', потому что',
    'потому что',
    'несмотря на то, что',
    'несмотря на',
    'после того как',
    'после того, как',
    'до того как',
    'до того, как',
    'перед тем как',
    'перед тем, как',
    'в течение',
]

RE_WHITESPACE_ONLY = re.compile(r'^\s+$')

TRANSLATOR_PUNCT_REMOVE = str.maketrans('', '', string.punctuation)

class Word(object):
    TYPE_NONE = 0
    TYPE_WORD = 1
    TYPE_HYPHENATED_WORD = 2
    TYPE_MWE = 3
    TYPE_WHITESPACE = 5
    TYPE_OTHER = 4
    VALID_TYPES = (TYPE_NONE, TYPE_WORD, TYPE_HYPHENATED_WORD, TYPE_MWE, TYPE_WHITESPACE, TYPE_OTHER)

    def __init__(self, tokens, word_type=TYPE_NONE):
        if isinstance(tokens, str):
            tokens = [tokens]
        self.tokens = tokens
        self.word_type = word_type

    def gettext(self, remove_accents=False, remove_punct=False):
        text = ''.join(self.tokens)
        if remove_accents:
            text = text.replace(COMBINING_ACCENT_CHAR, '')
        if remove_punct:
            text = text.translate(TRANSLATOR_PUNCT_REMOVE)
        return text

    def canonical(self):
        return self.gettext(remove_accents=True)

    def numtokens(self):
        return len(self.tokens)

    def getdata(self):
        return [self.word_type] + self.tokens

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
    def __init__(self):
        self._mwes = pygtrie.Trie()

    def add_mwe(self, mwe):
        self._mwes[mwe.lower()] = True

    def add_mwes(self, mwes):
        for mwe in mwes:
            self._mwes[mwe.lower()] = True

    def preprocess(self, text):
        return Preprocessor().preprocess(text)

    def tokenize(self, text):
        return Tokenizer().tokenize(text)

    def identifywords(self, tokens):
        queue = collections.deque(tokens)
        word_tokens = []
        words = []

        while len(queue) > 0:
            token = queue.popleft()
            word_type = Word.TYPE_OTHER
            word_tokens.append(token)

            if token[0] in RUS_ALPHABET_SET:
                word_type = Word.TYPE_WORD

                # Look ahead for hyphenated words or multi-word expressions
                if len(queue) > 0:
                    if queue[0] == HYPHEN_CHAR:
                        # Look for hyphenated words
                        word_type = Word.TYPE_HYPHENATED_WORD
                        word_tokens.append(queue.popleft())
                        if queue[0][0] in RUS_ALPHABET_SET:
                            word_tokens.append(queue.popleft())
                    else:
                        #  Look for multi-word expressions
                        lookahead = word_tokens.copy()
                        startpos = len(lookahead)
                        j = 0
                        while j < len(queue):
                            lookahead.append(queue[j])
                            expr = Word(tokens=lookahead).gettext(remove_accents=True)
                            expr = expr.lower()
                            if self._mwes.has_subtrie(expr):
                                j += 1
                                continue
                            elif self._mwes.has_key(expr):
                                word_type = Word.TYPE_MWE
                                for i in range(startpos, len(lookahead)):
                                    word_tokens.append(queue.popleft())
                            else:
                                break
            elif RE_WHITESPACE_ONLY.match(token):
                word_type = Word.TYPE_WHITESPACE

            word = Word(word_tokens, word_type=word_type)
            words.append(word)
            word_tokens = []

        return words

    def parse(self, text):
        nfkd_text = self.preprocess(text)
        tokens = self.tokenize(nfkd_text)
        words = self.identifywords(tokens)
        return words
