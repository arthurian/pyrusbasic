# -*- coding: utf-8 -*-
import unittest

from .parser import RussianParser, RussianTokenizer

class TestTokenizer(unittest.TestCase):
    def test_tokenizer_unaccented(self):
        tokenizer = RussianTokenizer()
        text = 'Все счастливые семьи похожи друг на друга, каждая несчастливая семья несчастлива по-своему.\n\n'
        expected_tokens = ['Все', ' ', 'счастливые', ' ', 'семьи', ' ', 'похожи', ' ', 'друг', ' ', 'на', ' ', 'друга', ', ', 'каждая', ' ', 'несчастливая', ' ', 'семья', ' ', 'несчастлива', ' ', 'по', '-', 'своему', '.\n\n', '']
        actual_tokens = tokenizer.tokenize(text)
        self.assertEqual(actual_tokens, expected_tokens)

    def test_tokenizer_accented(self):
        tokenizer = RussianTokenizer()
        text = 'Жила́-была́ на све́те лягу́шка-кваку́шка.'
        expected_tokens = ['Жила́', '-', 'была́', ' ', 'на', ' ', 'све́те', ' ', 'лягу́шка', '-', 'кваку́шка', '.', '']
        actual_tokens = tokenizer.tokenize(text)
        self.assertEqual(actual_tokens, expected_tokens)

class TestParser(unittest.TestCase):
    def test_parse_accented_and_hyphenated(self):
        parser = RussianParser()
        text = "све́те лягу́шка-кваку́шка.\n"
        words = parser.parse(text)
        self.assertEqual(words[0].gettext(), 'све́те')
        self.assertEqual(words[0].gettext(remove_accents=True), 'свете')
        self.assertEqual(words[1].gettext(), ' ')
        self.assertEqual(words[2].gettext(), 'лягу́шка-кваку́шка')
        self.assertEqual(words[2].gettext(remove_accents=True), 'лягушка-квакушка')
        self.assertEqual(len(words[2].tokens), 3)
        self.assertEqual(words[3].gettext(), ".\n")

    def test_mwe(self):
        parser = RussianParser()
        text = 'Он любил ее не потому, что она обладала неземной красотой.'
        expected_word_texts = ['Он', ' ', 'любил', ' ', 'ее', ' ', 'не', ' ', 'потому, что', ' ', 'она', ' ', 'обладала', ' ', 'неземной', ' ', 'красотой', '.']
        words = parser.parse(text)
        for i, word in enumerate(words):
            self.assertEqual(word.gettext(), expected_word_texts[i])

if __name__ == '__main__':
    unittest.main()
