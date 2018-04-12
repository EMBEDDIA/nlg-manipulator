import re
from core import EntityNameResolver

from format_numerals_fi import FinnishNumeralFormatter
from format_numerals_sv import SwedishNumeralFormatter
from format_numerals_en import EnglishNumeralFormatter

class CrimeEntityNameResolver(EntityNameResolver):

    value_type_re = re.compile(
        r'^([0-9_a-z]+?)(_normalized)?(_percentage)?(_change)?(?:(?:_grouped_by)(_time_place|_crime_time))?(_rank(?:_reverse)?)?$')

    def __init__(self):
        # [ENTITY:<group1>:<group2>] where group1 and group2 can contain anything but square brackets or double colon
        self._matcher = re.compile("\[(PLACE|TIME):([^\]:]*):([^\]]*)\]")
        self._formatters = {
            'fi': FinnishNumeralFormatter(),
            'sv': SwedishNumeralFormatter(),
            'en': EnglishNumeralFormatter(),
        }

    def is_entity(self, maybe_entity):
        # Match and convert the result to boolean
        try:
            return self._matcher.fullmatch(maybe_entity) is not None
        except TypeError:
            print("EntityNameResolver got a number: {} instead of a string".format(maybe_entity))

    def _parse_code(self, code):
        match = self._matcher.fullmatch(code)
        if not match:
            raise ValueError("Who value {} does not match entity regex".format(code))
        if not len(match.groups()) == 3:
            raise Exception("Invalid number of matched groups?!")
        return match.groups()

    def resolve_entity_type(self, code):
        return self._parse_code(code)[0]

    def resolve_surface_form(self, registry, random, language, slot):
        entity_type = self._parse_code(slot.value)[0]
        if entity_type == 'PLACE':
            return self._formatters[language].place(random, slot)
        elif entity_type == 'TIME':
            match = self.value_type_re.match(slot.fact.what_type)
            if match.group(4):
                return self._formatters[language].time.get(slot.fact.when_type + '_change')(random, slot)
            else:
                return self._formatters[language].time.get(slot.fact.when_type)(random, slot)
        raise ValueError("Unknown entity: {}".format(slot.value))
