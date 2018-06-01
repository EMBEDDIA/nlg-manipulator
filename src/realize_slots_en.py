import re
import logging
from dictionary_en import CRIME_TYPES, MONTHS, SMALL_CARDINALS, SMALL_ORDINALS

from core.template import LiteralSlot
log = logging.getLogger('root')


class EnglishRealizer():

    value_type_re = re.compile(
        r'([0-9_a-z]+?)(_normalized)?(?:(_mk_score|_mk_trend)|(_percentage)?(_change)?(?:(?:_grouped_by)(_time_place|_crime_time|_crime_place_year))?((?:_decrease|_increase)?_rank(?:_reverse)?)?)')

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
        }

    def _unit_base(self, slot):
        match = self.value_type_re.fullmatch(slot.value)
        unit, normalized, trend, percentage, change, grouped_by, rank = match.groups()
        if abs(slot.fact.what) == 1:
            # new_value = CRIME_TYPES.get(unit, {}).get('sg', unit)
            new_value = CRIME_TYPES.get(unit, unit)
        else:
            # new_value = CRIME_TYPES.get(unit, {}).get('pl', unit)
            new_value = CRIME_TYPES.get(unit, unit)
        return self._update_slot_value(slot, new_value)

    def _unit_percentage_points(self, slot):
        template = slot.parent
        prev_slot = template.components[template.components.index(slot) - 1]
        # If the previous slot contains a value larger than 10, we can just append the percent sign to the value.
        if prev_slot.slot_type == 'what' and prev_slot.fact.what > 10:
            current_value = prev_slot.value
            prev_slot.value = lambda x: current_value + "%"
            # Set the slot to contain an empty string, these are ignored later.
            return self._update_slot_value(slot, "")
        # Otherwise, use the written form
        else:
            return self._update_slot_value(slot, "percent")

    def _unit_percentage(self, slot):
        # The capture groups are:
        # (unit)(normalized)(percentage)(change)(grouped_by)(rank)
        match = self.value_type_re.fullmatch(slot.value)
        unit, normalized, trend, percentage, change, grouped_by, rank = match.groups()
        template = slot.parent
        idx = template.components.index(slot)
        added_slots = self._unit_percentage_points(slot)
        idx += added_slots + 1
        if slot.attributes.get('form') == 'short':
            return added_slots
        # template.add_slot(idx, LiteralSlot("of the " + CRIME_TYPES.get(unit, {}).get('pl', unit)))
        template.add_slot(idx, LiteralSlot("of the " + CRIME_TYPES.get(unit, unit)))
        added_slots += 1
        idx += 1
        return added_slots

    def _unit_change(self, slot):
        if slot.attributes.get('type', '') == 'comparison':
            return self._unit_comparison(slot)
        # The capture groups are:
        # (unit)(normalized)(percentage)(change)(grouped_by)(rank)
        match = self.value_type_re.fullmatch(slot.value)
        unit, normalized, trend, percentage, change, grouped_by, rank = match.groups()
        template = slot.parent
        idx = template.components.index(slot)
        # Check whether the following slot contains the value
        if template.components[idx + 1].slot_type == 'what':
            what_slot = template.components[idx + 1]
        elif template.components[idx - 1].slot_type == 'what':
            what_slot = template.components[idx - 1]
        else:
            log.error("Can't find the what slot!")
            return 0
        added_slots = 0
        self._update_slot_value(slot, CRIME_TYPES.get(unit, unit))
        idx += 1
        if slot.fact.what == 0:
            self._update_slot_value(what_slot, "stayed the same")
            # In the case of no change, we're done
            return added_slots
        elif slot.fact.what < 0 or (rank and '_decrease' in rank):
            template.add_slot(idx, LiteralSlot("decreased"))
        else:
            template.add_slot(idx, LiteralSlot("increased"))
        idx += 1
        # If we are talking about a rank value
        if rank:
            if what_slot.value == 1:
                self._update_slot_value(what_slot, "")
            template.add_slot(idx, LiteralSlot("the"))
            added_slots += 1
            # Skip over the what_slot
            idx += 2
            template.add_slot(idx, LiteralSlot("most"))
            idx += 1
            added_slots += 1
            return added_slots
        else:
            template.add_slot(idx, LiteralSlot("by"))
            added_slots += 1
            # Skip the value slot
            idx += 2
            # If we are talking about percentages
            if match.group(3):
                if what_slot.fact.what > 10:
                    current_value = what_slot.value
                    what_slot.value = lambda x: current_value + "%"
                else:
                    template.add_slot(idx, LiteralSlot("percent"))
                    added_slots += 1
                    idx += 1
        return added_slots

    def _unit_comparison(self, slot):
        # The capture groups are:
        # (unit)(normalized)(percentage)(change)(grouped_by)(rank)
        match = self.value_type_re.fullmatch(slot.value)
        unit, normalized, trend, percentage, change, grouped_by, rank = match.groups()
        template = slot.parent
        idx = template.components.index(slot)
        added_slots = 0
        # If compared to other crimes
        if grouped_by == '_time_place':
            self._update_slot_value(slot, "crimes")
        elif grouped_by == '_crime_time':
            self._update_slot_value(slot, "municipalities")
        else:
            raise Exception("This is impossible. The regex accepts only the two options above for group 5.")
        return added_slots

    def _unit_rank(self, slot):
        # Not implemented yet
        return 0

    def _ordinal(self, token):
        token = "{:n}".format(token)
        if token in SMALL_ORDINALS:
            # Use words for numbers up to 12
            # 0 shouldn't really be needed, but use 0th if it really has to be used
            return SMALL_ORDINALS[token]
        if len(token) > 1 and token[-2:] in ['11', '12', '13']:
            return token + "th"
        if token[-1] == '1':
            return token + "st"
        if token[-1] == '2':
            return token + "nd"
        if token[-1] == '3':
            return token + "rd"
        else:
            return token + "th"

    def _cardinal(self, token):
        token_str = "{:.2f}".format(token).rstrip("0").rstrip(".")
        return SMALL_CARDINALS.get(token_str, token_str)

    def _update_slot_value(self, slot, new_value):
        slot.value = lambda x: new_value
        return 0

    def _time_month(self, slot):
        # Not implemented yet
        return 0

    def _time_year(self, slot):
        year = slot.value
        added_slots = 0
        template = slot.parent
        idx = template.components.index(slot)
        new_slot = LiteralSlot("in")
        template.add_slot(idx, new_slot)
        added_slots += 1
        idx += 1
        if type(year) is not str:
            slot.value = lambda x: self._cardinal(year)
        return added_slots
