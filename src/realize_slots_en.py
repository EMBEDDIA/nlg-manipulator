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
            'month_change': self._time_change_month,
            'year_change': self._time_change_year
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

    def _time_month(self, random, slot):
        if slot.slot_type[:-2] == 'when':
            year, month = slot.value.split("M")
        elif slot.slot_type == 'time':
            year, month = slot.value[1:-1].split(":")[-1].split("M")
        added_slots = 0
        template = slot.parent
        idx = template.components.index(slot)
        # If the place is not realized at all, start the sentence with time instead, using either full or short form.
        if template.components[0].value == "":
            template.move_slot(idx, 0)
            idx = 0
            if slot.attributes['name_type'] == 'pronoun':
                slot.attributes['name_type'] = 'short'
        if (slot.attributes['name_type'] in ['full', 'short']) or (
                slot.attributes['name_type'] == 'pronoun' and random.rand() > 0.8):
            new_slot = LiteralSlot("in " + MONTHS[month])
            template.add_slot(idx, new_slot)
            added_slots += 1
            idx += 1
            self._update_slot_value(slot, year)
        elif slot.attributes['name_type'] == 'pronoun':
            reference_options = ["during the month", "also", "at the same time"]
            self._update_slot_value(slot, random.choice(reference_options))
        else:
            raise AttributeError("This is impossible. If we end up here, something is wrong (or has been changed carelessly) elsewhere in the code.")
        return added_slots

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
        # If the place is not realized at all, start the sentence with time instead, using either full or short form.
        if template.components[0].value == "":
            template.move_slot(idx, 0)
            idx = 0
            if slot.attributes['name_type'] == 'pronoun':
                slot.attributes['name_type'] = 'short'
        # The latter condition makes the system realize the full year roughly once in five sentences even
        # if the year hasn't changed.
        if (slot.attributes['name_type'] in ['full', 'short']) or (
                slot.attributes['name_type'] == 'pronoun' and random.rand() > 0.8):
            if slot.attributes['name_type'] == 'full':
                new_slot = LiteralSlot("in the year")
                template.add_slot(idx, new_slot)
                added_slots += 1
                idx += 1
            if year is None:
                self._update_slot_value(slot, 'x')
            elif type(year) is not str:
                self._update_slot_value(slot, self._cardinal(year))
            else:
                self._update_slot_value(slot, year)
        elif slot.attributes['name_type'] == 'pronoun':
            reference_options = ["in the same year", "also during the same year", "also"]
            self._update_slot_value(slot, random.choice(reference_options))
        else:
            raise AttributeError("This is impossible. If we end up here, something is wrong (or has been changed carelessly) elsewhere in the code.")
        return added_slots

    def _time_change_year(self, random, slot):
        time_matcher = re.compile("\[TIME:([^\]:]*):([^\]]*)\]")
        match = time_matcher.fullmatch(slot.value)
        added_slots = 0
        template = slot.parent
        idx = template.components.index(slot)
        if slot.attributes['name_type'] == 'full':
            new_slot = LiteralSlot("from")
            template.add_slot(idx, new_slot)
            added_slots += 1
            idx += 1
            template.add_slot(idx, LiteralSlot(match.group(1)))
            added_slots += 1
            idx += 1
            new_slot = LiteralSlot("to")
            template.add_slot(idx, new_slot)
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
            new_slot = LiteralSlot("from " + MONTHS[month1])
            template.add_slot(idx, new_slot)
            added_slots += 1
            idx += 1
            template.add_slot(idx, LiteralSlot(year1))
            added_slots += 1
            idx += 1
            new_slot = LiteralSlot("to " + MONTHS[month2])
            template.add_slot(idx, new_slot)
            added_slots += 1
            idx += 1
            template.add_slot(idx, LiteralSlot(year2))
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
        prep = slot.attributes.get('prep', "in") + " "
        if place_type == 'C' and place == 'fi':
            place = "Finland"
        if place_type in ["C", "M"]:
            if slot.attributes['name_type'] == 'full':
                self._update_slot_value(slot, prep + place)
            elif random.rand() < 0.5:
                if place_type == 'M':
                    self._update_slot_value(slot, prep + "the municipality")
                elif place_type == 'C':
                    self._update_slot_value(slot, prep + "the country")
                else:
                    raise Exception(
                        "This is impossible. If we end up here, something is wrong (or has been changed carelessly) elsewhere in the code.")
            else:
                self._update_slot_value(slot, "")
        return 0
