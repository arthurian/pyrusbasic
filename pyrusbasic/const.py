# -*- coding: utf-8 -*-

# Pairs of upper and lowercase cyrillic letters in the russian alphabet
RUS_ALPHABET_LIST = (
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
)
RUS_ALPHABET_SET = set(RUS_ALPHABET_LIST)
RUS_ALPHABET_STR = ''.join(RUS_ALPHABET_LIST)

# Combining diacritics
COMBINING_ACCENT_CHAR = '\u0301'   # Diacritic used to mark stress on russian words
COMBINING_DIURESIS_CHAR = '\u0308' # Diacritic used with the seventh letter of the russian alphabet (ё)
COMBINING_BREVE_CHAR = '\u0306'    # Diacritic used with the eleventh letter of the russian alphabet (й)

# Hyphens and dashes
HYPHEN_CHAR = '\u002D'  # Punctuation used to join components of a word
EN_DASH_CHAR = '\u2013' # May be used interchangeably with hyphen or em-dash depending on context
EM_DASH_CHAR = '\u2014' # Punctuation used to separate words in a sentence

# Quotation marks
QUOTE_ANGLE_LEFT = '\u00AB'
QUOTE_ANGLE_RIGHT = '\u00BB'
QUOTE_RAISED_LEFT = '\u201e'
QUOTE_RAISED_RIGHT = '\u201c'

# Some common multi-word expressions
COMMON_MWES = (
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
)
