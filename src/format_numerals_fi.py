import re

from core.template import LiteralSlot


class FinnishNumeralFormatter():

    SMALL_ORDINALS = {
        '1': "ensimmäinen",
        '2': "toinen",
        '3': "kolmas",
        '4': "neljäs",
        '5': "viides",
        '6': "kuudes",
        '7': "seitsemäs",
        '8': "kahdeksas",
        '9': "yhdeksäs",
        '10': "kymmenes",
    }

    SMALL_CARDINALS = {
        '1': "yksi",
        '2': "kaksi",
        '3': "kolme",
        '4': "neljä",
        '5': "viisi",
        '6': "kuusi",
        '7': "seitsemän",
        '8': "kahdeksan",
        '9': "yhdeksän",
        '10': "kymmenen",
    }

    MONTHS = {
        '1': "tammikuu",
        '2': "helmikuu",
        '3': "maaliskuu",
        '4': "huhtikuu",
        '5': "toukokuu",
        '6': "kesäkuu",
        '7': "heinäkuu",
        '8': "elokuu",
        '9': "syyskuu",
        '10': "lokakuu",
        '11': "marraskuu",
        '12': "joulukuu",
    }

    UNITS = {
        'seats': {
            'sg': "paikka",
            'pl': "paikat"
        },
        'votes': {
            'sg': "ääni",
            'pl': "äänet"
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
            'month': self._time_month,
            'year': self._time_year,
        }

    def _unit_set_value(self, slot, new_value):
        slot.value = lambda x: new_value
        # If case hasn't been defined, assume accusative
        if slot.attributes.get('case', 'accusative') == 'accusative':
            self._unit_set_accusative(slot)
        return 0

    def _unit_base(self, slot):
        match = self.value_type_re.match(slot.value)
        unit = match.group(2)
        new_value = self.UNITS.get(unit, {}).get('sg', unit)
        return self._unit_set_value(slot, new_value)

    def _unit_percentage(self, slot):
        match = self.value_type_re.match(slot.value)
        template = slot.parent
        idx = template.components.index(slot)
        added_slots = 0
        self._unit_set_value(slot, "prosentti")
        idx += 1
        if slot.attributes.get('form') == 'short':
            return added_slots
        new_slot = LiteralSlot(self.UNITS[match.group(2)]['pl'])
        new_slot.attributes['case'] = 'elative'
        template.add_component(idx, new_slot)
        idx += 1
        added_slots += 1
        return added_slots

    def _unit_change(self, slot):
        match = self.value_type_re.match(slot.value)
        template = slot.parent
        idx = template.components.index(slot)
        # If the value_type starts with percentage_ or total_
        if match.group(1) and match.group(1) == 'percentage_':
            added_slots = self._unit_set_value(slot, "prosenttiyksikkö")
        else:
            added_slots = self._unit_base(slot)
        if slot.attributes.get('form') == 'short':
            return added_slots
        idx += 1
        if slot.fact.what_2 < 0:
            template.add_component(idx, LiteralSlot("vähemmän"))
        else:
            template.add_component(idx, LiteralSlot("enemmän"))
        added_slots += 1
        idx += 1
        # For the percentage values we also need to realize the original unit
        if match.group(1) == 'percentage_':
            new_slot = LiteralSlot(self.UNITS[match.group(2)]['pl'])
            new_slot.attributes['case'] = 'partitive'
            template.add_component(idx, new_slot)
            added_slots += 1
            idx += 1
        return added_slots

    def _unit_rank(self, slot):
        match = self.value_type_re.match(slot.value)
        template = slot.parent
        idx = template.components.index(slot)
        added_slots = 0
        prev_slot = template.components[idx - 1]
        if prev_slot.slot_type == 'what_2':
            # If the rank is first, the actual numeral isn't realized at all
            if slot.fact.what_2 == 1:
                prev_slot.value = lambda x: ""
            # If the numeral is realized, it needs to be an ordinal and in the translative case
            else:
                prev_slot.value = lambda x: self._ordinal(prev_slot.fact.what_2)
                if 'case' not in prev_slot.attributes.keys():
                    prev_slot.attributes['case'] = 'translative'
        # This also works for _rank_reverse, since the difference is communicated using different verbs.
        # ToDo: This is still not finished, probably needs more stuff to work properly in all cases.
        slot.value = lambda x: "eniten"
        idx += 1
        new_slot = LiteralSlot(self.UNITS[match.group(2)]['pl'])
        new_slot.attributes['case'] = 'partitive'
        template.add_component(idx, new_slot)
        added_slots += 1
        idx += 1
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
        if abs(slot.fact.what_2) == 1:
            slot.attributes['case'] = 'genitive'
            if prev_slot.slot_type == 'what_2':
                prev_slot.attributes['case'] = 'genitive'
        # "kaksi/kolme paikkaa/ääntä"
        else:
            slot.attributes['case'] = 'partitive'
            if prev_slot.slot_type == 'what_2':
                prev_slot.attributes['case'] = 'nominative'

    def _ordinal(self, token):
        token = "{}".format(token)
        if token in self.SMALL_ORDINALS:
            return self.SMALL_ORDINALS[token]
        return token + "."

    def _cardinal(self, token):
        token_str = "{}".format(token)
        if "." in token_str:
            token_str = re.sub(r'(\d+).(\d+)', r'\1,\2', token_str)
        if token_str in self.SMALL_CARDINALS:
            return self.SMALL_CARDINALS[token_str]
        return token_str

    def _time_year(self, slot):
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
        if type(year) is not str:
            slot.value = lambda x: self._cardinal(year)
        return added_slots

    def _time_month(self, slot):
        # Here I'm assuming that the when_type will use format yyyy/mm. Fix as needed when the format is finalized.
        year, __, month = slot.value.partition("/")
        # Remove possible zero-padding
        if month[0] == "0":
            month = month[1:]
        added_slots = 0
        template = slot.parent
        idx = template.components.index(slot)
        new_slot = LiteralSlot(self.MONTHS[month])
        new_slot.attributes['case'] = 'inessive'
        template.add_component(idx, new_slot)
        added_slots += 1
        idx += 1
        slot.value = lambda x: year
        return added_slots
