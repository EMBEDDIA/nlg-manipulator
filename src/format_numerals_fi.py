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
        },
        '1_offences_and_infractions_total_all_offences':{
            'sg': "1-rikos", #ToDo: this is not the correct name, fix
            'pl': "1-rikokset"
        },
        '4_endangerment_of_traffic_safety_hitandrun_traffic_infraction_all_offences':{
            'sg': "4-liikennerikos", #ToDo: this is not the correct name, fix
            'pl': "4-liikennerikokset"
        },
        'traffic_infraction_violation_of_social_welfare_legislation_on_road_traffic_all_offences':{
            'sg': "liikennerikos", #ToDo: this is not the correct name, fix
            'pl': "liikennerikokset"
        }
    }

    value_type_re = re.compile(
        r'^([0-9_a-z]+?)(_normalized)?(_percentage)?(_change)?(?:(?:_grouped_by)(_time_place|_crime_time))?(_rank(?:_reverse)?)?$')

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
        unit = match.group(1)
        new_value = self.UNITS.get(unit, {}).get('sg', unit)
        return self._unit_set_value(slot, new_value)

    def _unit_percentage(self, slot):
        # The capture groups are:
        # (unit)(normalized)(percentage)(change)(grouped_by)(rank)
        match = self.value_type_re.match(slot.value)
        unit = match.group(1)
        template = slot.parent
        idx = template.components.index(slot)
        added_slots = 0
        self._unit_set_value(slot, "prosentti")
        idx += 1
        if slot.attributes.get('form') == 'short':
            return added_slots
        new_slot = LiteralSlot(self.UNITS.get(unit, {}).get('pl', unit))
        new_slot.attributes['case'] = 'elative'
        template.add_component(idx, new_slot)
        idx += 1
        added_slots += 1
        return added_slots

    def _unit_change(self, slot):
        # The capture groups are:
        # (unit)(normalized)(percentage)(change)(grouped_by)(rank)
        match = self.value_type_re.match(slot.value)
        unit = match.group(1)
        template = slot.parent
        idx = template.components.index(slot)
        added_slots = 0
        value_plus_unit_length = 2
        # If type change_rank
        if match.group(6):
            # rikosten määrä kasvoi viidenneksi eniten
            new_slots = self._unit_rank(slot)
            added_slots += new_slots
            value_plus_unit_length += new_slots
        elif match.group(3):
            # rikosten määrä kasvoi viisi prosenttiyksikköä
            new_slots = self._unit_set_value(slot, "prosenttiyksikkö")
            added_slots += new_slots
            value_plus_unit_length += new_slots
        else:
            # rikosten määrä kasvoi viidellä
            prev_slot = template.components[idx - 1]
            prev_slot.attributes['case'] = 'adessive'
            slot.value = lambda x: ""
        # Move the index to the slot before the value + unit
        idx += added_slots - 1
        if match.group(2):
            template.add_component(idx, LiteralSlot("suhteellinen"))
            added_slots += 1
            idx += 1
        new_slot = LiteralSlot(self.UNITS.get(unit, {}).get('pl', unit))
        new_slot.attributes['case'] = 'genitive'
        template.add_component(idx, new_slot)
        added_slots += 1
        idx += 1
        template.add_component(idx, LiteralSlot("määrä kasvoi"))
        added_slots += 1
        idx += 1
        idx += value_plus_unit_length
        if match.group(5):
            template.add_component(idx, LiteralSlot("muihin"))
            added_slots += 1
            idx += 1
            if match.group(5) == '_time_place':
                template.add_component(idx, LiteralSlot("rikoksiin verrattuna"))
                added_slots += 1
                idx += 1
            else:
                template.add_component(idx, LiteralSlot("alueisiin verrattuna"))
                added_slots += 1
                idx += 1
        return added_slots

    def _unit_rank(self, slot):
        # The capture groups are:
        # (unit)(normalized)(percentage)(change)(grouped_by)(rank)
        match = self.value_type_re.match(slot.value)
        unit = match.group(1)
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
        if match.group(6) == "_rank":
            slot.value = lambda x: "eniten"
        elif match.group(6) == "_rank_reverse":
            slot.value = lambda x: "vähiten"
        else:
            raise Exception("This is impossible. The regex accepts only the two options above for this group.")
        idx += 1
        # If talking about changes, we will do the rest in the change handler
        if match.group(4):
            return added_slots
        new_slot = LiteralSlot(self.UNITS.get(unit, {}).get('pl', unit))
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
        token = "{:n}".format(token)
        if token in self.SMALL_ORDINALS:
            return self.SMALL_ORDINALS[token]
        return token + "."

    def _cardinal(self, token):
        token_str = "{:n}".format(token)
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
        if year is None:
            slot.value = lambda x: 'x'
        elif type(year) is not str:
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
