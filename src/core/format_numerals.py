from .pipeline import NLGPipelineComponent

from format_numerals_fi import FinnishNumeralFormatter
from format_numerals_sv import SwedishNumeralFormatter
from format_numerals_en import EnglishNumeralFormatter

import logging
import re
log = logging.getLogger('root')


class NumeralFormatter(NLGPipelineComponent):

    def __init__(self):
        self._formatters = {
            'fi': FinnishNumeralFormatter(),
            'sv': SwedishNumeralFormatter(),
            'en': EnglishNumeralFormatter(),
        }
        self._formatter = None
        self._default_numeral = lambda x: "{:n}".format(x)
        self._default_unit = lambda x: None
        self._default_time = lambda x: None

    def run(self, registry, random, language, document_plan):
        """
        Run this pipeline component.
        """
        log.info("Fixing numerals")
        self._formatter = self._formatters[language[:2]]
        self._recurse(document_plan)
        return (document_plan, )

    def _recurse(self, this):
        try:
            # Try to use the current root as a non-leaf.
            log.debug("Visiting non-leaf '{}'".format(this))
            # Use indexes to iterate through the children since the template slots may be edited, added or replaced
            # during iteration. Ugly, but will do for now.
            idx = 0
            while idx < len(this.children):
                slots_added = self._recurse(this.children[idx])
                if slots_added:
                    idx += slots_added
                idx += 1
        except AttributeError as ex:
            # Had no children, must be a leaf node
            log.debug("Visiting leaf {}".format(this))
            try:
                slot_type = this.slot_type
            except (AttributeError):
                log.info("Got an AttributeError when checking slot_type in format_numerals. Probably not a slot.")
                slot_type = 'n/a'
            if slot_type[:-2] == 'what':
                added_slots = self._realize_value(this)
                return added_slots
            elif slot_type[:-2] == 'when':
                added_slots = self._realize_time(this)
                return added_slots
            elif slot_type[:-2] == 'what_type':
                added_slots = self._realize_unit(this)
                return added_slots

    def _realize_value(self, slot):
        try:
            num_type = slot.attributes.get('num_type')
            value = slot.value
            if type(value) is str:
                return None
            modified_value = self._formatter.numerals.get(num_type, self._default_numeral)(value)
            slot.value = lambda x: modified_value
        except AttributeError:
            log.error("Error in value realization of slot {}".format(slot))
            pass

    def _realize_unit(self, slot):
        value_type_re = re.compile(r'(percentage_|total_)?([a-z]+)(_change)?(_rank(_reverse)?)?')
        match = value_type_re.match(slot.value)
        try:
            if match.group(4):
                new_slots = self._formatter.units.get('rank', self._default_unit)(slot)
            elif match.group(3):
                new_slots = self._formatter.units.get('change', self._default_unit)(slot)
            elif match.group(1) == 'percentage_':
                new_slots = self._formatter.units.get('percentage', self._default_unit)(slot)
            else:
                new_slots = self._formatter.units.get('base', self._default_unit)(slot)
            return new_slots
        except AttributeError:
            log.error("Error in unit realization of slot {}".format(slot))
            return 0

    def _realize_time(self, slot):
        # slot_suffix is either '_1' or '_2'
        slot_suffix = slot.slot_type[-2:]
        try:
            # Check the when_type corresponding to the slot_suffix of the current slot, just to be sure. Usually the
            # type should be same for both suffixes
            when_type = getattr(slot.fact, 'when_type' + slot_suffix)
            added_slots = self._formatter.time.get(when_type, self._default_time)(slot)
            return added_slots
        except AttributeError:
            log.error("Error in time realization of slot {}".format(slot))
            return 0
