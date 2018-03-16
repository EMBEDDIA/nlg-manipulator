import re

from core.template import LiteralSlot


class EnglishNumeralFormatter():

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

    value_type_re = re.compile(r'(percentage_|total_)?([a-z]+)(_change)?(_rank(_reverse)?)?')

    def __init__(self):

        self.numerals = {
            'ordinal': self._ordinal,
            'cardinal': self._cardinal,
        }

        self.units = {
            'base': self._unit_base,

            'percentage': self._unit_percentage,

            'change': self._unit_change,

        }

        self.time = {

        }

    def _unit_base(self, slot):
        match = self.value_type_re.match(slot.value)
        unit = match.group(2)
        if abs(slot.fact.what_2) == 1:
            new_value = self.UNITS[unit]['sg']
        else:
            new_value = self.UNITS[unit]['pl']
        return self._update_slot_value(slot, new_value)

    def _unit_percentage_points(self, slot):
        template = slot.parent
        prev_slot = template.components[template.components.index(slot) - 1]
        # If the previous slot contains a value, we can just append the percent sign to the value.
        if prev_slot.slot_type == 'what_2':
            current_value = prev_slot.value
            prev_slot.value = lambda x: current_value + "%"
            template.components.remove(slot)
            return -1
        # Otherwise, use the written form
        else:
            return self._update_slot_value(slot, "percent")

    def _unit_percentage(self, slot):
        match = self.value_type_re.match(slot.value)
        template = slot.parent
        idx = template.components.index(slot)
        added_slots = self._unit_percentage_points(slot)
        idx += added_slots + 1
        if slot.attributes.get('form') == 'short':
            return added_slots
        template.add_component(idx, LiteralSlot("of the " + self.UNITS[match.group(2)]['pl']))
        added_slots += 1
        idx += 1
        return added_slots

    def _unit_change(self, slot):
        match = self.value_type_re.match(slot.value)
        template = slot.parent
        idx = template.components.index(slot)
        # If the value_type starts with percentage_ or total_
        if match.group(1) and match.group(1) == 'percentage_':
            added_slots = self._update_slot_value(slot, "percentage points")
            idx += 1
        else:
            # Note: in this case we must not increase the idx in order to have the quantifier _before_ the unit
            # e.g. "5 more votes" instead of "5 votes more"
            added_slots = self._unit_base(slot)
        if slot.attributes.get('form') == 'short':
            return added_slots
        if slot.fact.what_2 < 0:
            template.add_component(idx, LiteralSlot("less"))
        else:
            template.add_component(idx, LiteralSlot("more"))
        added_slots += 1
        idx += 1
        # For the percentage values we also need to realize the original unit
        if match.group(1) == 'percentage_':
            new_slot = LiteralSlot(self.UNITS[match.group(2)]['pl'])
            template.add_component(idx, new_slot)
            added_slots += 1
            idx += 1
        return added_slots

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
