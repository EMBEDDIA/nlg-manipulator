# define the path that leads to language files

from language import dictionary_en
from language import dictionary_fi
from language import dictionary_de
from language import dictionary_hr

REALIZERS = {
    'en': dictionary_en,
    'fi': dictionary_fi,
    'de': dictionary_de,
    'hr': dictionary_hr,
}

MORPHOLOGIES = {
    'hr',
}