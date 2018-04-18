import re
import logging
from core.template import LiteralSlot
from dictionary_fi import CRIME_TYPES, MONTHS, SMALL_CARDINALS, SMALL_ORDINALS
log = logging.getLogger('root')

class FinnishRealizer():

    value_type_re = re.compile(r'([0-9_a-z]+?)(_normalized)?(_percentage)?(_change)?(?:(?:_grouped_by)(_time_place|_crime_time|_crime_place_year))?((?:_decrease|_increase)?_rank(?:_reverse)?)?')

    def __init__(self):

        self.numerals = {
            'ordinal': self._ordinal,
            'cardinal': self._cardinal,
        }

        self.units = {
            'base': self._unit_base,
            'percentage': self._unit_percentage,
            'change': self._unit_change,
            'rank': self._unit_rank,
        }

        self.time = {
            'month': self._time_month,
            'year': self._time_year,
            'month_change': self._time_change_month,
            'year_change': self._time_change_year
        }

    def _update_slot_value(self, slot, new_value):
        slot.value = lambda x: new_value
        return 0

    def _unit_set_value(self, slot, new_value):
        slot.value = lambda x: new_value
        # If case hasn't been defined, assume accusative
        if slot.attributes.get('case', 'accusative') == 'accusative':
            self._unit_set_accusative(slot)
        return 0

    def _unit_base(self, slot):
        match = self.value_type_re.fullmatch(slot.value)
        unit, normalized, percentage, change, grouped_by, rank = match.groups()
        template = slot.parent
        idx = template.components.index(slot)
        added_slots = 0
        content = CRIME_TYPES.get(unit, {}).get('sg', unit)
        try:
            unit, non_case_idx = content
            words = unit.split()
        except ValueError:
            words = content.split()
        if len(words) == 1:
            added = self._unit_set_value(slot, words[0])
        else:
            case = slot.attributes.get('case', 'partitive')
            self._update_slot_value(slot, "")
            added = self._add_slots(template, idx, content, case)
        added_slots += added
        idx += added + 1
        if normalized:
            template.add_component(idx, LiteralSlot("tuhatta asukasta kohti"))
            added_slots += 1
            idx += 1
        return added_slots


    def _unit_percentage(self, slot):
        match = self.value_type_re.fullmatch(slot.value)
        unit, normalized, percentage, change, grouped_by, rank = match.groups()
        template = slot.parent
        idx = template.components.index(slot)
        added_slots = 0
        self._unit_set_value(slot, "prosentti")
        idx += 1
        if slot.attributes.get('form') == 'short':
            return added_slots
        # new_slot = LiteralSlot(CRIME_TYPES.get(unit, {}).get('pl', unit))
        added = self._add_slots(template, idx, CRIME_TYPES.get(unit, {}).get('pl', unit), case='elative')
        idx += added
        added_slots += added
        return added_slots

    def _unit_change(self, slot):
        match = self.value_type_re.fullmatch(slot.value)
        unit, normalized, percentage, change, grouped_by, rank = match.groups()
        template = slot.parent
        idx = template.components.index(slot)
        # Check whether the following slot contains the value
        if template.components[idx - 1].slot_type == 'what':
            what_slot = template.components[idx - 1]
        else:
            log.error("The Finnish change template should have a value slot preceding a unit slot!")
            return 0
        added_slots = 0
        # Move the pointer to the value slot
        idx -= 1
        # new_slot = LiteralSlot(CRIME_TYPES.get(unit, {}).get('pl', unit))
        added = self._add_slots(template, idx, CRIME_TYPES.get(unit, {}).get('pl', unit), case='genitive')
        idx += added
        added_slots += added

        template.add_component(idx, LiteralSlot("määrä"))
        added_slots += 1
        idx += 1

        if normalized:
            template.add_component(idx, LiteralSlot("suhteessa asukaslukuun"))
            added_slots += 1
            idx += 1

        if slot.fact.what > 0:
            template.add_component(idx, LiteralSlot("kasvoi"))
        elif slot.fact.what < 0:
            template.add_component(idx, LiteralSlot("laski"))
        else:
            self._update_slot_value(slot, "säilyi ennallaan")
            # Clear the value slot
            self._update_slot_value(what_slot, "")
            return added_slots
        added_slots += 1
        # Jump over the what_slot
        idx += 2

        # The base unit
        if rank:
            # rikosten määrä kasvoi viidenneksi eniten
            new_slots = self._unit_rank(slot)
            added_slots += new_slots
        elif percentage:
            # rikosten määrä kasvoi viisi prosenttiyksikköä
            new_slots = self._unit_set_value(slot, "prosenttiyksikkö")
            added_slots += new_slots
        else:
            # rikosten määrä kasvoi viidellä
            prev_slot = template.components[idx - 1]
            prev_slot.attributes['case'] = 'adessive'
            slot.value = lambda x: ""
        idx += 1

        # The end comparison
        if grouped_by:
            template.add_component(idx, LiteralSlot("muihin"))
            added_slots += 1
            idx += 1
            if grouped_by == '_time_place':
                template.add_component(idx, LiteralSlot("rikostyyppeihin verrattuna"))
                added_slots += 1
                idx += 1
            elif grouped_by == '_crime_time':
                template.add_component(idx, LiteralSlot("alueisiin verrattuna"))
                added_slots += 1
                idx += 1
            elif grouped_by == 'crime_place_year':
                template.add_component(idx, LiteralSlot("kuukausiin verrattuna"))
                added_slots += 1
                idx += 1
            else:
                raise Exception("This is impossible. The regex accepts only the above options for this group.")
        return added_slots

    def _unit_rank(self, slot):
        match = self.value_type_re.fullmatch(slot.value)
        unit, normalized, percentage, change, grouped_by, rank = match.groups()
        template = slot.parent
        idx = template.components.index(slot)
        added_slots = 0
        prev_slot = template.components[idx - 1]
        if not change and grouped_by == '_time_place':
            template.add_component(idx - 1, LiteralSlot("kaikista rikoksista"))
            added_slots += 1
            idx += 1
        if prev_slot.slot_type == 'what':
            # If the rank is first, the actual numeral isn't realized at all
            if slot.fact.what == 1:
                prev_slot.value = lambda x: ""
            # If the numeral is realized, it needs to be an ordinal and in the translative case
            else:
                prev_slot.value = lambda x: self._ordinal(prev_slot.fact.what)
                if 'case' not in prev_slot.attributes.keys():
                    prev_slot.attributes['case'] = 'translative'
        if rank in ['_rank', '_increase_rank', '_decrease_rank']:
            slot.value = lambda x: "eniten"
        elif rank == '_rank_reverse':
            slot.value = lambda x: "vähiten"
        else:
            raise Exception("This is impossible. The regex accepts only the above options for this group.")
        idx += 1
        # If talking about changes, we will do the rest in the change handler
        if change:
            return added_slots
        added = self._add_slots(template, idx, CRIME_TYPES.get(unit, {}).get('pl', unit), case='partitive')
        idx += added
        added_slots += added
        return added_slots

    def _add_slots(self, template, idx, content, case=None):
        added_slots = 0
        # Assume the the content is a tuple consisting of a string and a list of indexes not to be inflected
        try:
            words, non_case_idx = content
            words = words.split()
            for content_idx, word in enumerate(words):
                new_slot = LiteralSlot(word)
                if case and content_idx not in non_case_idx:
                    new_slot.attributes['case'] = case
                template.add_component(idx + added_slots, new_slot)
                added_slots += 1
        # If the content doesn't contain a list of indexes, assume that all words in it should be inflected:
        except ValueError:
            words = content.split()
            for word in words:
                new_slot = LiteralSlot(word)
                if case :
                    new_slot.attributes['case'] = case
                template.add_component(idx + added_slots, new_slot)
                added_slots += 1
        return added_slots

    def _unit_set_accusative(self, slot):
        """
        Set the cases for the slot (and the previous slot, if it contains a value) to the proper case for accusative.
        This is genitive for both when the value is 1, and nominative for the numeral and partitive tor the unit in
        other cases.
        :param slot:
        :return:
        """
        prev_slot = slot.parent.components[slot.parent.components.index(slot) - 1]
        # "yhden paikan/äänen/etc."
        if abs(slot.fact.what) == 1:
            slot.attributes['case'] = 'genitive'
            if prev_slot.slot_type == 'what':
                prev_slot.attributes['case'] = 'genitive'
        # "kaksi/kolme paikkaa/ääntä"
        else:
            slot.attributes['case'] = 'partitive'
            if prev_slot.slot_type == 'what':
                prev_slot.attributes['case'] = 'nominative'

    def _ordinal(self, token):
        token = "{:n}".format(token)
        if token in SMALL_ORDINALS:
            return SMALL_ORDINALS[token]
        return token + "."

    def _cardinal(self, token):
        token_str = "{:.2f}".format(token).rstrip("0").rstrip(".")
        if "." in token_str:
            token_str = re.sub(r'(\d+).(\d+)', r'\1,\2', token_str)
        if token_str in SMALL_CARDINALS:
            return SMALL_CARDINALS[token_str]
        return token_str

    def _time_year(self, random, slot):
        if slot.slot_type[:-2] == 'when':
            year = slot.value
        elif slot.slot_type == 'time':
            # If we are realizing a {time} slot, we can simply use either of the time values as the year
            # Here we're choosing the latter one
            year = slot.value[1:-1].split(":")[-1]
        else:
            log.error("Weird slot type '{}' sent to be realized as a year value. Hopefully it's valid.".format(slot.value))
            year = slot.value
        added_slots = 0
        template = slot.parent
        idx = template.components.index(slot)
        if 'case' in slot.attributes.keys():
            new_slot = LiteralSlot("vuosi")
            new_slot.attributes['case'] = slot.attributes['case']
            slot.attributes['case'] = 'nominative'
        else:
            new_slot = LiteralSlot("vuonna")
        template.add_component(idx, new_slot)
        added_slots += 1
        idx += 1
        if year is None:
            slot.value = lambda x: 'x'
        elif type(year) is not str:
            slot.value = lambda x: self._cardinal(year)
        else:
            self._update_slot_value(slot, year)
        return added_slots

    def _time_month(self, random, slot):
        if slot.slot_type[:-2] == 'when':
            year, month = slot.value.split("M")
        elif slot.slot_type == 'time':
            year, month = slot.value[1:-1].split(":")[-1].split("M")
        added_slots = 0
        template = slot.parent
        idx = template.components.index(slot)
        new_slot = LiteralSlot(MONTHS[month])
        new_slot.attributes['case'] = 'inessive'
        template.add_component(idx, new_slot)
        added_slots += 1
        idx += 1
        slot.value = lambda x: year
        return added_slots

    def _time_change_year(self, random, slot):
        time_matcher = re.compile("\[TIME:([^\]:]*):([^\]]*)\]")
        match = time_matcher.fullmatch(slot.value)
        added_slots = 0
        template = slot.parent
        idx = template.components.index(slot)
        if slot.attributes['name_type'] == 'full':
            if 'case' in slot.attributes.keys():
                new_slot = LiteralSlot("aikaväli")
                new_slot.attributes['case'] = slot.attributes['case']
                template.add_component(idx, new_slot)
                added_slots += 1
                idx += 1
                self._update_slot_value(slot, match.group(1) + "-" + match.group(2))
                slot.attributes['case'] = 'nominative'
            else:
                new_slot = LiteralSlot("vuosi")
                new_slot.attributes['case'] = 'elative'
                template.add_component(idx, new_slot)
                added_slots += 1
                idx += 1
                template.add_component(idx, LiteralSlot(match.group(1)))
                added_slots += 1
                idx += 1
                new_slot = LiteralSlot("vuosi")
                new_slot.attributes['case'] = 'illative'
                template.add_component(idx, new_slot)
                added_slots += 1
                idx += 1
                self._update_slot_value(slot, match.group(2))
        elif slot.attributes['name_type'] == 'short':
            self._update_slot_value(slot, match.group(1) + "-" + match.group(2))
            slot.attributes['case'] = 'nominative'
        else:
            self._update_slot_value(slot, "")
        return added_slots

    def _time_change_month(self, random, slot):
        time_matcher = re.compile("\[TIME:([^\]:]*):([^\]]*)\]")
        match = time_matcher.fullmatch(slot.value)
        year1, month1 = match.group(1).split('M')
        year2, month2 = match.group(2).split('M')
        added_slots = 0
        template = slot.parent
        idx = template.components.index(slot)
        if slot.attributes['name_type'] == 'full':
            if 'case' in slot.attributes.keys():
                new_slot = LiteralSlot("aikaväli")
                new_slot.attributes['case'] = slot.attributes['case']
                template.add_component(idx, new_slot)
                added_slots += 1
                idx += 1
                self._update_slot_value(slot, month1 + "/" + year1 + "-" + month2 + "/" + year2)
                slot.attributes['case'] = 'nominative'
            else:
                new_slot = LiteralSlot(MONTHS[month1])
                new_slot.attributes['case'] = 'elative'
                template.add_component(idx, new_slot)
                added_slots += 1
                idx += 1
                template.add_component(idx, LiteralSlot(year1))
                added_slots += 1
                idx += 1
                new_slot = LiteralSlot(MONTHS[month2])
                new_slot.attributes['case'] = 'illative'
                template.add_component(idx, new_slot)
                added_slots += 1
                idx += 1
                template.add_component(idx, LiteralSlot(year2))
                added_slots += 1
                idx += 1
        elif slot.attributes['name_type'] == 'short':
            self._update_slot_value(slot, month1 + "/" + year1 + "-" + month2 + "/" + year2)
            slot.attributes['case'] = 'nominative'
        else:
            self._update_slot_value(slot, "")
        return added_slots

    def place(self, random, slot):
        place_matcher = re.compile("\[PLACE:([^\]:]*):([^\]]*)\]")
        entity_code = slot.value
        place_type, place = place_matcher.match(entity_code).groups()
        if place_type == 'C' and place == 'fi':
            place = "Suomi"
        if place_type in ["C", "D", "M", "P"]:
            if slot.attributes['name_type'] == 'full':
                self._update_slot_value(slot, place)
            else:
                self._update_slot_value(slot, "paikkakunta")
        return 0
