# define the path that leads to language files
from typing import Dict

from language import dictionary_de, dictionary_en, dictionary_fi, dictionary_hr

REALIZERS: Dict[str, str] = {
    "en": dictionary_en,
    "fi": dictionary_fi,
    "de": dictionary_de,
    "hr": dictionary_hr,
}

MORPHOLOGIES = {
    "hr",
}

MANIPULATORS = {
    "en",
    "fi",
}

BERTS = {
    #"en": "bert-base-uncased",
    "en": "../finest-bert-pytorch",
    "fi": "../finest-bert-pytorch",
    #"fi": "../bert-base-finnish-cased-v1",
}