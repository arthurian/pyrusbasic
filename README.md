# PyRusBasic

Python package that provides basic tokenization and parsing of Russian language texts. 

**Functionality:**

- Splits input text into russian words and non-russian words.
- Normalizes input text into NFKD form for consistent parsing and output.
- Preserves accent marks, punctuation, and white space from the input text so that it can be recreated if necessary.
- Converts tokens into `Word` objects, identifying hyphenated words and multi-word expressions for later analysis.

## Usage

Install via pip:

```sh
$ pip install git+https://github.com/arthurian/pyrusbasic.git#egg=pyrusbasic
```

Example:

```python
import pyrusbasic
parser = pyrusbasic.Parser()
text = 'Все счастливые семьи похожи друг на друга, каждая несчастливая семья несчастлива по-своему.'
words = parser.parse(text)
print([str(w) for w in words])

['Все', ' ', 'счастливые', ' ', 'семьи', ' ', 'похожи', ' ', 'друг', ' ', 'на', ' ', 'друга', ', ', 'каждая', ' ', 'несчастливая', ' ', 'семья', ' ', 'несчастлива', ' ', 'по-своему', '.']
```

Example with multi-word expressions:

```python
import pyrusbasic
parser = pyrusbasic.Parser()
parser.add_mwe('Несмотря на то, что')
parser.add_mwe('еще не много')
text = 'Несмотря на то, что еще не много времени прошло с тех пор, как князь Андрей оставил Россию, он много изменился за это время.'
words = parser.parse(text)
print([str(w) for w in words])

['Несмотря на то, что', ' ', 'еще не много', ' ', 'времени', ' ', 'прошло', ' ', 'с', ' ', 'тех', ' ', 'пор', ', ', 'как', ' ', 'князь', ' ', 'Андрей', ' ', 'оставил', ' ', 'Россию', ', ', 'он', ' ', 'много', ' ', 'изменился', ' ', 'за', ' ', 'это', ' ', 'время', '.']```
