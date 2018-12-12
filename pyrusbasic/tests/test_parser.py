# -*- coding: utf-8 -*-
import unittest
import pyrusbasic.const

class TestWord(unittest.TestCase):
    def test_accents(self):
        tests = [
            ['све́те', 'свете'],
            ['любо́вь', 'любовь'],
            ['вещество́', 'вещество'],
            ['мото́р', 'мотор'],
        ]
        for test in tests:
            (accented, unaccented) = test
            word = pyrusbasic.Word(accented)
            self.assertEqual(accented, word.gettext())
            self.assertEqual(accented, str(word))
            self.assertEqual(unaccented, word.gettext(remove_accents=True))
            self.assertEqual(unaccented, word.canonical())
            self.assertEqual(1, word.numtokens())


class TestTokenizer(unittest.TestCase):
    def test_tokenizer_unaccented(self):
        tokenizer = pyrusbasic.Tokenizer()
        text = 'Все счастливые семьи похожи друг на друга, каждая несчастливая семья несчастлива по-своему.\n\n'
        expected_tokens = ['Все', ' ', 'счастливые', ' ', 'семьи', ' ', 'похожи', ' ', 'друг', ' ', 'на', ' ', 'друга', ', ', 'каждая', ' ', 'несчастливая', ' ', 'семья', ' ', 'несчастлива', ' ', 'по', '-', 'своему', '.\n\n']
        actual_tokens = tokenizer.tokenize(text)
        self.assertEqual(expected_tokens, actual_tokens)

    def test_tokenizer_accented(self):
        tokenizer = pyrusbasic.Tokenizer()
        text = 'Жила́-была́ на све́те лягу́шка-кваку́шка.'
        expected_tokens = ['Жила́', '-', 'была́', ' ', 'на', ' ', 'све́те', ' ', 'лягу́шка', '-', 'кваку́шка', '.']
        actual_tokens = tokenizer.tokenize(text)
        self.assertEqual(expected_tokens, actual_tokens)


class TestParser(unittest.TestCase):
    def test_parse_accented_and_hyphenated(self):
        parser = pyrusbasic.Parser()
        text = "све́те лягу́шка-кваку́шка.\n"
        words = parser.parse(text)
        self.assertEqual('све́те', words[0].gettext())
        self.assertEqual(' ', words[1].gettext())
        self.assertEqual('лягу́шка-кваку́шка', words[2].gettext(), )
        self.assertEqual(3, words[2].numtokens())
        self.assertEqual( ".\n", words[3].gettext())

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
            self.assertEqual(hyphenated_word ,words[0].gettext())
            self.assertEqual(3, len(words[0].tokens))

    def test_unique_mwes(self):
        parser = pyrusbasic.Parser()
        mwes = [
            'потому же',
            'потому, что',
            'несмотря на то, что',
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
            'description': 'MWE at the beginning of the sentence with capitalized first letter: Несмотря на то, что',
        },{
            'input': 'Да все потому же',
            'output': ['Да', ' ', 'все', ' ', 'потому же'],
            'description': 'MWE in the middle of the phrase: потому же',
        }]
        for test in tests:
            expected = test['output']
            words = parser.parse(test['input'])
            for i, word in enumerate(words):
                self.assertEqual(expected[i], word.gettext(), test['description'])

    def test_prefixed_mwes(self):
        parser = pyrusbasic.Parser()
        mwes = [
            'несмотря на',
            'несмотря на то, что',
            'до того',
            'до того как',
            'перед тем, как',
        ]
        parser.add_mwes(mwes)
        tests = [{
            'input': 'Несмотря на серьзёную болезнь...',
            'output': ['Несмотря на', ' ', 'серьзёную', ' ', 'болезнь', '...'],
            'description': 'MWE at the beginning: Несмотря на',
        },{
            'input': 'возможна, несмотря на то, что фактов',
            'output': ['возможна', ', ', 'несмотря на то, что', ' ', 'фактов'],
            'description': 'MWE in the middle: несмотря на то, что',
        },{
            'input': 'до того как союз.',
            'output': ['до того как', ' ', 'союз', '.'],
            'description': 'MWE at the beginning: до того как',
        },{
            'input': 'Им не до того.',
            'output': ['Им', ' ', 'не', ' ', 'до того', '.'],
            'description': 'MWE near the end of the phrase: до того',
        },{
            'input': 'Что ты делала перед тем, как уснула?',
            'output': ['Что', ' ', 'ты', ' ', 'делала', ' ', 'перед тем, как', ' ', 'уснула', '?'],
            'description': 'MWE in the middle: перед тем, как'
        }]
        for test in tests:
            expected = test['output']
            words = parser.parse(test['input'])
            for i, word in enumerate(words):
                self.assertEqual(expected[i], word.gettext(), test['description'])

    def test_mwe_case_sensitive(self):
        parser = pyrusbasic.Parser(mwe_case_sensitive=True)
        mwe_with_initial_uppercase_letter = 'Несмотря на'
        parser.add_mwe(mwe_with_initial_uppercase_letter)
        text = 'Несмотря на серьзёную болезнь...'
        words = parser.parse(text)
        self.assertEqual(mwe_with_initial_uppercase_letter, words[0].gettext())

    def test_add_mwe(self):
        parser = pyrusbasic.Parser(mwe_case_sensitive=False)
        parser.add_mwe('Несмотря на то, что')
        parser.add_mwe('еще не много')
        text = 'Несмотря на то, что еще не много времени прошло с тех пор, как князь Андрей оставил Россию...'
        words = parser.parse(text)
        self.assertEqual('Несмотря на то, что', words[0].gettext())
        self.assertEqual(' ', words[1].gettext())
        self.assertEqual('еще не много', words[2].gettext())
        self.assertEqual(' ', words[3].gettext())
        self.assertEqual('времени', words[4].gettext())

    def test_text_can_be_reconstructed(self):
        parser = pyrusbasic.Parser(mwe_case_sensitive=False)
        parser.add_mwe('потому, что')
        text = 'А если же я и провела хорошо каникулы, так это потому, что занималась наукой и вела себя хорошо.'
        words = parser.parse(text)
        reconstructed_text = ''.join(map(str, words))
        self.assertEqual(text, reconstructed_text)


if __name__ == '__main__':
    unittest.main()
