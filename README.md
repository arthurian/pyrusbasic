# PyRusBasic

Python package that provides basic tokenization and parsing of Russian language texts so that individual words and expressions can be analyzed.

**Functionality:**

- Converts tokens into `Word` objects.
- Preserves accent marks, punctuation, and white space in the tokenized result so that the original text.
- Groups hyphenated words and multi-word expressions so they can be treated as a unit.

## Usage

Install via pip:

```sh
$ pip install git+https://github.com/arthurian/pyrusbasic.git#egg=pyrusbasic
```

Example sentence parsed into words:

```python
import pyrusbasic
parser = pyrusbasic.Parser()
text = 'Все счастливые семьи похожи друг на друга, каждая несчастливая семья несчастлива по-своему.'
words = parser.parse(text)
print([str(w) for w in words])

['Все', ' ', 'счастливые', ' ', 'семьи', ' ', 'похожи', ' ', 'друг', ' ', 'на', ' ', 'друга', ', ', 'каждая', ' ', 'несчастливая', ' ', 'семья', ' ', 'несчастлива', ' ', 'по-своему', '.']
```

Example with _multi-word expressions_ (mwes):

```python
import pyrusbasic
parser = pyrusbasic.Parser()
parser.add_mwe('Несмотря на то, что')
parser.add_mwe('еще не много')
text = 'Несмотря на то, что еще не много времени прошло с тех пор, как князь Андрей оставил Россию, он много изменился за это время.'
words = parser.parse(text)
print([str(w) for w in words])

['Несмотря на то, что', ' ', 'еще не много', ' ', 'времени', ' ', 'прошло', ' ', 'с', ' ', 'тех', ' ', 'пор', ', ', 'как', ' ', 'князь', ' ', 'Андрей', ' ', 'оставил', ' ', 'Россию', ', ', 'он', ' ', 'много', ' ', 'изменился', ' ', 'за', ' ', 'это', ' ', 'время', '.']
```
