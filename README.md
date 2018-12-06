# Russian Parser

This is a basic parser for Russian language texts.

## Usage

```sh
$ pip install 

```

```python
from russianparser.parser import RussianParser
parser = RussianParser()
text = 'Все счастливые семьи похожи друг на друга, каждая несчастливая семья несчастлива по-своему.'
parser.parse(text)
```

Output:

```text
[[1, 'Все'], [5, ' '], [1, 'счастливые'], [5, ' '], [1, 'семьи'], [5, ' '], [1, 'похожи'], [5, ' '], [1, 'друг'], [5, ' '], [1, 'на'], [5, ' '], [1, 'друга'], [4, ', '], [1, 'каждая'], [5, ' '], [1, 'несчастливая'], [5, ' '], [1, 'семья'], [5, ' '], [1, 'несчастлива'], [5, ' '], [2, 'по', '-', 'своему'], [4, '.']]
```
