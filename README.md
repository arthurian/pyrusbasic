# PyRusBasic

Python package that provides basic tokenization and parsing of Russian language texts so that individual words and expressions can be analyzed.

**Functionality:**

- Converts tokens into `Word` objects.
- Preserves accent marks, punctuation, and white space.
- Groups hyphenated words and multi-word expressions.

## Usage

Install via pip:

```sh
$ pip install git+https://github.com/arthurian/pyrusbasic.git#egg=pyrusbasic
```

Example sentence parsed into words:

```python
import pyrusbasic
tokenizer = pyrusbasic.WordTokenizer()
text = 'Все счастливые семьи похожи друг на друга, каждая несчастливая семья несчастлива по-своему.'
wordlist = tokenizer.tokenize(text)
print([str(w) for w in wordlist.words])

['Все', ' ', 'счастливые', ' ', 'семьи', ' ', 'похожи', ' ', 'друг', ' ', 'на', ' ', 'друга', ', ', 'каждая', ' ', 'несчастливая', ' ', 'семья', ' ', 'несчастлива', ' ', 'по-своему', '.']
```

Example with _multi-word expressions_ (mwes):

```python
import pyrusbasic
tokenizer = pyrusbasic.WordTokenizer()
tokenizer.add_mwe('Несмотря на то, что')
tokenizer.add_mwe('еще не много')
text = 'Несмотря на то, что еще не много времени прошло с тех пор, как князь Андрей оставил Россию, он много изменился за это время.'
wordlist = tokenizer.tokenize(text)
print([str(w) for w in wordlist.words])

['Несмотря на то, что', ' ', 'еще не много', ' ', 'времени', ' ', 'прошло', ' ', 'с', ' ', 'тех', ' ', 'пор', ', ', 'как', ' ', 'князь', ' ', 'Андрей', ' ', 'оставил', ' ', 'Россию', ', ', 'он', ' ', 'много', ' ', 'изменился', ' ', 'за', ' ', 'это', ' ', 'время', '.']
```
