import re
import logging

from core.template import LiteralSlot
log = logging.getLogger('root')


class EnglishRealizer():

    SMALL_ORDINALS = {
        '1': "first",
        '2': "second",
        '3': "third",
        '4': "fourth",
        '5': "fifth",
        '6': "sixth",
        '7': "seventh",
        '8': "eighth",
        '9': "ninth",
        '10': "tenth",
        '11': "eleventh",
        '12': "twelfth",
    }

    SMALL_CARDINALS = {
        '1': "one",
        '2': "two",
        '3': "three",
        '4': "four",
        '5': "five",
        '6': "six",
        '7': "seven",
        '8': "eight",
        '9': "nine",
        '10': "ten",
    }

    UNITS = {
        'seats': {
            'sg': "seat",
            'pl': "seats"
        },
        'votes': {
            'sg': "vote",
            'pl': "votes"
        }
    }

    value_type_re = re.compile(
        r'([0-9_a-z]+?)(_normalized)?(_percentage)?(_change)?(?:(?:_grouped_by)(_time_place|_crime_time|_crime_place_year))?((?:_decrease|_increase)?_rank(?:_reverse)?)?')

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
        unit = match.group(1)
        if abs(slot.fact.what) == 1:
            new_value = self.UNITS.get(unit, {}).get('sg', unit)
        else:
            new_value = self.UNITS.get(unit, {}).get('pl', unit)
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
        unit = match.group(1)
        template = slot.parent
        idx = template.components.index(slot)
        added_slots = self._unit_percentage_points(slot)
        idx += added_slots + 1
        if slot.attributes.get('form') == 'short':
            return added_slots
        template.add_component(idx, LiteralSlot("of the " + self.UNITS.get(unit, {}).get('pl', unit)))
        added_slots += 1
        idx += 1
        return added_slots

    def _unit_change(self, slot):
        if slot.attributes.get('type', '') == 'comparison':
            return self._unit_comparison(slot)
        # The capture groups are:
        # (unit)(normalized)(percentage)(change)(grouped_by)(rank)
        match = self.value_type_re.fullmatch(slot.value)
        unit = match.group(1)
        template = slot.parent
        idx = template.components.index(slot)
        what_slot = None
        # Check whether the following slot contains the value
        if template.components[idx + 1].slot_type == 'what':
            what_slot = template.components[idx + 1]
        else:
            log.error("The English change template should have a value slot following a unit slot!")
            return 0
        added_slots = 0
        self._update_slot_value(slot, self.UNITS.get(unit, {}).get('pl', unit))
        idx += 1
        if slot.fact.what == 0:
            self._update_slot_value(what_slot, "stayed the same")
            # In the case of no change, we're done
            return added_slots
        elif slot.fact.what < 0:
            template.add_component(idx, LiteralSlot("decreased"))
        else:
            template.add_component(idx, LiteralSlot("increased"))
        idx += 1
        # If we are talking about a rank value
        if match.group(6):
            if what_slot.value == 1:
                self._update_slot_value(what_slot, "")
            template.add_component(idx, LiteralSlot("the"))
            added_slots += 1
            # Skip over the what_slot
            idx += 2
            if match.group(6) == "_rank":
                template.add_component(idx, LiteralSlot("most"))
            elif match.group(6) == "_rank_reverse":
                template.add_component(idx, LiteralSlot("least"))
            else:
                raise Exception("This is impossible. The regex accepts only the two options above for group 6.")
            idx += 1
            added_slots += 1
            return added_slots
        else:
            template.add_component(idx, LiteralSlot("by"))
            added_slots += 1
            # Skip the value slot
            idx += 2
            # If we are talking about percentages
            if match.group(3):
                if what_slot.fact.what > 10:
                    current_value = what_slot.value
                    what_slot.value = lambda x: current_value + "%"
                else:
                    template.add_component(idx, LiteralSlot("percent"))
                    added_slots += 1
                    idx += 1
        return added_slots

    def _unit_comparison(self, slot):
        # The capture groups are:
        # (unit)(normalized)(percentage)(change)(grouped_by)(rank)
        match = self.value_type_re.fullmatch(slot.value)
        grouped_by = match.group(5)
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
        if token in self.SMALL_ORDINALS:
            # Use words for numbers up to 12
            # 0 shouldn't really be needed, but use 0th if it really has to be used
            return self.SMALL_ORDINALS[token]
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
        token = "{:n}".format(token)
        return self.SMALL_CARDINALS.get(token, token)

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
        template.add_component(idx, new_slot)
        added_slots += 1
        idx += 1
        if type(year) is not str:
            slot.value = lambda x: self._cardinal(year)
        return added_slots
