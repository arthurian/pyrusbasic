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

EN_DASH_CHAR = '\u2013'
HYPHEN_CHAR = '\u002D'

DEFAULT_MWES = [
    'потому что',
    'потому, что',
    ',потому что',
]

RE_WHITESPACE_ONLY = re.compile(r'^\s+$')

TRANSLATOR_PUNCT_REMOVE = str.maketrans('', '', string.punctuation)

class RussianWord(object):
    TYPE_WORD = 1
    TYPE_HYPHENATED_WORD = 2
    TYPE_MWE = 3
    TYPE_WHITESPACE = 5
    TYPE_OTHER = 4

    def __init__(self, tokens=None, word_type=None):
        self.tokens = []
        self.word_type = None

        if tokens is not None:
            self.tokens.extend(tokens)
        if word_type is not None:
            self.word_type = word_type

    def gettext(self, remove_accents=False, remove_punct=False):
        text = "".join(self.tokens)
        if remove_accents:
            text = text.replace(COMBINING_ACCENT_CHAR, '')
        if remove_punct:
            text = text.translate(TRANSLATOR_PUNCT_REMOVE)
        return text

    def getdata(self):
        return [self.word_type] + self.tokens

    def __repr__(self):
        return str(self.getdata())

    def __str__(self):
        return self.gettext()

class RussianPreprocessor(object):
    def preprocess(self, text):
        text = text.replace(EN_DASH_CHAR, HYPHEN_CHAR)
        nfkd_form = unicodedata.normalize('NFKD', text)
        return nfkd_form

class RussianTokenizer(object):
    def tokenize(self, text):
        # First pass at splitting text into groups of russian characters, including accents, and then all others.
        # Note the intention is to preserve upper/lower case characters and all whitespace, punctuation, etc
        pattern = "([^" + RUS_ALPHABET_STR + COMBINING_ACCENT_CHAR + COMBINING_BREVE_CHAR + "]+)"
        tokens = re.split(pattern, text)
        return tokens

class RussianParser(object):
    def __init__(self):
        self._mwes = pygtrie.Trie()
        self.add_mwes(DEFAULT_MWES)

    def add_mwes(self, multi_word_exprs):
        for mwe in multi_word_exprs:
            self._mwes[mwe] = True

    def preprocess(self, text):
        return RussianPreprocessor().preprocess(text)

    def tokenize(self, text):
        return RussianTokenizer().tokenize(text)

    def identifywords(self, tokens):
        queue = collections.deque(tokens)
        word_tokens = []
        words = []

        while len(queue) > 0:
            token = queue.popleft()
            # Skip empty tokens
            if len(token) == 0:
                continue

            word_type = RussianWord.TYPE_OTHER
            word_tokens.append(token)

            if token[0] in RUS_ALPHABET_SET:
                word_type = RussianWord.TYPE_WORD

                # Look ahead for hyphenated words or multi-word expressions
                if len(queue) > 0:
                    if queue[0] == HYPHEN_CHAR:
                        # Look for hyphenated words
                        word_type = RussianWord.TYPE_HYPHENATED_WORD
                        word_tokens.append(queue.popleft())
                        if queue[0][0] in RUS_ALPHABET_SET:
                            word_tokens.append(queue.popleft())
                    else:
                        #  Look for multi-word expressions
                        lookahead = word_tokens.copy()
                        j = 0
                        while j < len(queue):
                            lookahead.append(queue[j])
                            expr = "".join(lookahead)
                            if self._mwes.has_key(expr):
                                for i in range(1, len(lookahead)):
                                    word_tokens.append(queue.popleft())
                                    word_type = RussianWord.TYPE_MWE
                            elif self._mwes.has_subtrie(expr):
                                j += 1
                                continue
                            else:
                                break
            elif RE_WHITESPACE_ONLY.match(token):
                word_type = RussianWord.TYPE_WHITESPACE

            word = RussianWord(word_tokens, word_type=word_type)
            words.append(word)
            word_tokens = []

        return words

    def parse(self, text):
        nfkd_text = self.preprocess(text)
        tokens = self.tokenize(nfkd_text)
        words = self.identifywords(tokens)
        return words
