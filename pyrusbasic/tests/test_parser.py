# -*- coding: utf-8 -*-
import unittest
import pyrusbasic.const

class TestWord(unittest.TestCase):
    def test_accents(self):
        tests = [
            ['све́те', 'свете'],
            ['лягу́шка-кваку́шка', 'лягушка-квакушка'],
        ]
        for (accented, unaccented) in tests:
            word = pyrusbasic.Word(accented)
            self.assertEqual(word.gettext(), accented)
            self.assertEqual(str(word), accented)
            self.assertEqual(word.gettext(remove_accents=True), unaccented)
            self.assertEqual(word.canonical(), unaccented)
            self.assertEqual(word.numtokens(), 1)

class TestTokenizer(unittest.TestCase):
    def test_tokenizer_unaccented(self):
        tokenizer = pyrusbasic.Tokenizer()
        text = 'Все счастливые семьи похожи друг на друга, каждая несчастливая семья несчастлива по-своему.\n\n'
        expected_tokens = ['Все', ' ', 'счастливые', ' ', 'семьи', ' ', 'похожи', ' ', 'друг', ' ', 'на', ' ', 'друга', ', ', 'каждая', ' ', 'несчастливая', ' ', 'семья', ' ', 'несчастлива', ' ', 'по', '-', 'своему', '.\n\n']
        actual_tokens = tokenizer.tokenize(text)
        self.assertEqual(actual_tokens, expected_tokens)

    def test_tokenizer_accented(self):
        tokenizer = pyrusbasic.Tokenizer()
        text = 'Жила́-была́ на све́те лягу́шка-кваку́шка.'
        expected_tokens = ['Жила́', '-', 'была́', ' ', 'на', ' ', 'све́те', ' ', 'лягу́шка', '-', 'кваку́шка', '.']
        actual_tokens = tokenizer.tokenize(text)
        self.assertEqual(actual_tokens, expected_tokens)

class TestParser(unittest.TestCase):
    def test_parse_accented_and_hyphenated(self):
        parser = pyrusbasic.Parser()
        text = "све́те лягу́шка-кваку́шка.\n"
        words = parser.parse(text)
        self.assertEqual(words[0].gettext(), 'све́те')
        self.assertEqual(words[1].gettext(), ' ')
        self.assertEqual(words[2].gettext(), 'лягу́шка-кваку́шка')
        self.assertEqual(words[2].numtokens(), 3)
        self.assertEqual(words[3].gettext(), ".\n")

    def test_hyphenated(self):
        parser = pyrusbasic.Parser()
        hyphenated = [
            'всё-таки',
            'из-за',
            'из-под',
            'по-своему',
            'по-твоему',
            'по-английски',
            'по-русски',
        ]
        for hyphenated_word in hyphenated:
            words = parser.parse(hyphenated_word)
            self.assertEqual(words[0].gettext(), hyphenated_word)
            self.assertEqual(len(words[0].tokens), 3)

    def test_unique_mwes(self):
        parser = pyrusbasic.Parser()
        mwes = [
            'потому, что',
            'несмотря на то, что',
            'до того как',
        ]
        parser.add_mwes(mwes)
        tests = [{
            'input': 'Он любил ее не потому, что она обладала неземной красотой.',
            'output': ['Он', ' ', 'любил', ' ', 'ее', ' ', 'не', ' ', 'потому, что', ' ', 'она', ' ', 'обладала', ' ', 'неземной', ' ', 'красотой', '.'],
            'description': 'MWE in the middle of the sentence: потому, что'
        },{
            'input': 'Мы шли долго, но не устали, несмотря на то, что погода не благоприятствовала прогулке.',
            'output': ['Мы', ' ', 'шли', ' ', 'долго', ', ', 'но', ' ', 'не', ' ', 'устали', ', ', 'несмотря на то, что', ' ', 'погода', ' ', 'не', ' ', 'благоприятствовала', ' ', 'прогулке', '.'],
            'description': 'MWE in the middle of the sentence: несмотря на то, что',
        },{
            'input': 'Несмотря на то, что чья-то карета...',
            'output': ['Несмотря на то, что', ' ', 'чья-то', ' ', 'карета', '...'],
            'description': 'MWE at the beginning of the sentence (capitalized first letter)',
        },{
            'input': 'до того как союз.',
            'output': ['до того как', ' ', 'союз', '.'],
            'description': 'MWE at the beginning of a phrase, not capitalized',
        }]
        for test in tests:
            expected = test['output']
            words = parser.parse(test['input'])
            for i, word in enumerate(words):
                self.assertEqual(word.gettext(), expected[i], test['description'])

    def test_sub_mwes(self):
        parser = pyrusbasic.Parser()
        mwes = [
            'несмотря на',
            'несмотря на то, что',
        ]
        parser.add_mwes(mwes)
        tests = [{
            'input': 'Несмотря на серьзёную болезнь...',
            'output': ['Несмотря на', ' ', 'серьзёную', ' ', 'болезнь', '...'],
            'description': 'MWE that IS a prefix of another',
        },{
            'input': 'возможна, несмотря на то, что фактов',
            'output': ['возможна', ', ', 'несмотря на то, что', ' ', 'фактов'],
            'description': 'MWE that is NOT a prefix of another MWE',
        }]
        for test in tests:
            expected = test['output']
            words = parser.parse(test['input'])
            for i, word in enumerate(words):
                self.assertEqual(word.gettext(), expected[i], test['description'])


    def test_add_mwe(self):
        parser = pyrusbasic.Parser()
        parser.add_mwe('Несмотря на то, что')
        parser.add_mwe('еще не много')
        text = 'Несмотря на то, что еще не много времени прошло с тех пор, как князь Андрей оставил Россию, он много изменился за это время.'
        words = parser.parse(text)
        self.assertEqual(words[0].gettext(), 'Несмотря на то, что')
        self.assertEqual(words[1].gettext(), ' ')
        self.assertEqual(words[2].gettext(), 'еще не много')
        self.assertEqual(words[3].gettext(), ' ')
        self.assertEqual(words[4].gettext(), 'времени')

if __name__ == '__main__':
    unittest.main()
