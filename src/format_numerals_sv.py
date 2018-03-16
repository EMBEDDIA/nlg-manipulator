import re

from core.template import LiteralSlot


class SwedishNumeralFormatter():

    SMALL_ORDINALS = {
        # Först = adverbial form, which I think is the way we always want to do this
        # Otherwise, it will need to go through omorphi
        '1': "först",
        '2': "andra",
        '3': "tredje",
        '4': "fjärde",
        '5': "femte",
        '6': "sjätte",
        '7': "sjunde",
        '8': "åttonde",
        '9': "nionde",
        '10': "tionde",
        '11': "elfte",
        '12': "tolfte",
    }

    UNITS = {
        'seats': {
            'sg': "plats",
            'pl': "platser",
            'sgdef': "platsen",
            'pldef': "platserna",
        },
        'votes': {
            'sg': "röst",
            'pl': "röster",
            'sgdef': "rösten",
            'pldef': "rösterna",
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

            'rank': self._unit_rank,

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

    def _unit_percentage(self, slot):
        match = self.value_type_re.match(slot.value)
        template = slot.parent
        idx = template.components.index(slot)
        added_slots = 0
        self._update_slot_value(slot, "procent")
        idx += 1
        if slot.attributes.get('form') == 'short':
            return added_slots
        template.add_component(idx, LiteralSlot("av " + self.UNITS[match.group(2)]['pldef']))
        added_slots += 1
        idx += 1
        return added_slots

    def _unit_change(self, slot):
        match = self.value_type_re.match(slot.value)
        template = slot.parent
        idx = template.components.index(slot)
        # If the value_type starts with percentage_ or total_
        if match.group(1) and match.group(1) == 'percentage_':
            added_slots = self._update_slot_value(slot, "procentenheter")
            idx += 1
        else:
            # Note: in this case we must not increase the idx in order to have the quantifier _before_ the unit
            # e.g. "5 fler röster" instead of "5 röster fler"
            added_slots = self._unit_base(slot)
        if slot.attributes.get('form') == 'short':
            return added_slots
        if slot.fact.what_2 < 0:
            template.add_component(idx, LiteralSlot("färre"))
        else:
            template.add_component(idx, LiteralSlot("fler"))
        added_slots += 1
        idx += 1
        # For the percentage values we also need to realize the original unit
        if match.group(1) == 'percentage_':
            new_slot = LiteralSlot(self.UNITS[match.group(2)]['pl'])
            template.add_component(idx, new_slot)
            added_slots += 1
            idx += 1
        return added_slots

    def _unit_rank(self, slot):
        # Not implemented yet
        return 0

    def _cardinal(self, token):
        token_str = "{:n}".format(token)
        if "." in token_str:
            token_str = re.sub(r'(\d+).(\d+)', r'\1,\2', token_str)
        return token_str

    def _ordinal(self, token):
        token = "{:n}".format(token)
        if token in self.SMALL_ORDINALS:
            # Words for numbers up to 12
            return self.SMALL_ORDINALS[token]
        if len(token) > 1 and token[-2] in ['11', '12']:
            return token + ":e"
        if token[-1] in ['1', '2']:
            return token + ":a"
        else:
            return token + ":e"

    def _update_slot_value(self, slot, new_value):
        slot.value = lambda x: new_value
        return 0
