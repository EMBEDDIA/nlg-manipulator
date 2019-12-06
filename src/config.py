# define the path that leads to language files
import sys
sys.path.append('./language')

import dictionary_en
import dictionary_fi
import dictionary_de
import dictionary_hr

REALIZERS = {
    'en': dictionary_en,
    'fi': dictionary_fi,
    'de': dictionary_de,
    'hr': dictionary_hr,
}

MORPHOLOGIES = {
    'hr',
}