# Russian Parser

This is a basic parser for Russian language texts to tokenize and identify russian words for later analysis.

**Key features:**

- Parsing preserves accent marks, white space, and punctuation from the input.
- Normalizes unicode characters in NFKD form so that output is consistent.
- Groups tokens together into Word objects for hyphenated words and multi-word expressions.

## Usage

Install via pip:

```sh
$ pip install git+https://github.com/arthurian/russianparser.git#egg=russianparser
```

Basic example:

```
import russianparser
parser = russianparser.Parser()
words = parser.parse('Все счастливые семьи похожи друг на друга, каждая несчастливая семья несчастлива по-своему.')
print([str(w) for w in words])

['Все', ' ', 'счастливые', ' ', 'семьи', ' ', 'похожи', ' ', 'друг', ' ', 'на', ' ', 'друга', ', ', 'каждая', ' ', 'несчастливая', ' ', 'семья', ' ', 'несчастлива', ' ', 'по-своему', '.']
```

Example with multi-word expressions:

```
import russianparser
parser = russianparser.Parser()
parser.add_mwe('Несмотря на то, что')
parser.add_mwe('еще не много')
words = parser.parse('Несмотря на то, что еще не много времени прошло с тех пор, как князь Андрей оставил Россию, он много изменился за это время.')
print([str(w) for w in words])

['Несмотря на то, что', ' ', 'еще не много', ' ', 'времени', ' ', 'прошло', ' ', 'с', ' ', 'тех', ' ', 'пор', ', ', 'как', ' ', 'князь', ' ', 'Андрей', ' ', 'оставил', ' ', 'Россию', ', ', 'он', ' ', 'много', ' ', 'изменился', ' ', 'за', ' ', 'это', ' ', 'время', '.']```
