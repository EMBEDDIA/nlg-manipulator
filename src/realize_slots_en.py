import re
import logging
from dictionary_en import MONTHS, SMALL_CARDINALS, SMALL_ORDINALS, INDICATORS

from core.template import LiteralSlot
log = logging.getLogger('root')


class EnglishRealizer():

    from paramconfig import value_type_re
    value_type_re = re.compile(value_type_re)

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
            'trend': self._unit_trend,
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
        template = slot.parent
        idx = template.components.index(slot)
        added_slots = 0
        what_type = slot.fact.what_type.split('cp_')
        if what_type[0] == "rt12":
            if slot.attributes.get('form', '') != 'short':
                # Add the predicate _before_ the value
                template.add_slot(idx - 1, LiteralSlot("the growth rate from previous year was"))
                added_slots += 1
                idx += 1

        elif what_type[0] == "rt1":
            if slot.attributes.get('form', '') != 'short':
                # Add the predicate _before_ the value
                template.add_slot(idx - 1, LiteralSlot("the growth rate from previous month was"))
                added_slots += 1
                idx += 1
        
        elif what_type[0] == "hicp2015":
            if slot.attributes.get('form', '') != 'short':
                # Add the predicate _before_ the value
                template.add_slot(idx - 1, LiteralSlot("the HICP value was"))
                added_slots += 1
                idx += 1

        new_value = INDICATORS.get(what_type[1], what_type[1])

        self._update_slot_value(slot, new_value)
        idx += 1

        template.add_slot(idx-1, LiteralSlot("for"))
        added_slots += 1
        idx += 1

        # if normalized:
        #     template.add_slot(idx, LiteralSlot("per 1,000 people"))
        #     idx += 1
        #     added_slots += 1

        return added_slots

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
        match = self.value_type_re.fullmatch(slot.value)
        unit, normalized, trend, percentage, change, grouped_by, rank = match.groups()
        template = slot.parent
        idx = template.components.index(slot)
        if rank and '_reverse' in rank:
            log.error("_rank_reverse values found in combination with change. These shouldn't exist, because we can't know whether the top ranking cases mean the largest decrease or the smallest increase")
        # Check whether the following slot contains the value
        # Check whether the preceding slot contains the value
        if template.components[idx - 1].slot_type == 'what':
            what_slot = template.components[idx - 1]
        else:
            log.error("The Finnish change template should have a value slot preceding a unit slot!")
            return 0
        added_slots = 0
        # The short form is used within brackets as an elaboration
        if slot.attributes.get('form', '') == 'short':
            # A special case for when the change is zero
            if slot.fact.what == 0:
                self._update_slot_value(what_slot, "")
                self._update_slot_value(slot, "no change")
            else:
                unit_str = "case"
                if what_slot.value != 1:
                    unit_str += "s"
                self._update_slot_value(slot, unit_str)
                idx += 1
                if slot.fact.what < 0:
                    template.add_slot(idx - 1, LiteralSlot("less"))
                else:
                    template.add_slot(idx - 1, LiteralSlot("more"))
                idx += 1
                added_slots += 1
                if normalized:
                    template.add_slot(idx, LiteralSlot("per 1,000 people"))
                    idx += 1
                    added_slots += 1
            return added_slots

        # The beginning of the full form realisation
        # Move the idx pointer back to add slots before the numerical value
        idx -= 1

        template.add_slot(idx, LiteralSlot("the number of"))
        added_slots += 1
        idx += 1

        template.add_slot(idx, LiteralSlot(CRIME_TYPES.get(unit, unit)))
        idx += 1
        added_slots += 1

        # Specify the normalisation if needed
        if normalized and 'no_normalization' not in slot.attributes.keys():
            if not (rank or percentage):
                # with rank or percentage values we don't need to specify the exact normalizing factor
                # absolute normalized values don't make sense without this information
                template.add_slot(idx, LiteralSlot("per 1,000 people"))
                added_slots += 1
                idx += 1

        # Specify the predicate
        if 'no_normalization' not in slot.attributes.keys():
            if slot.fact.what < 0 or (rank and '_decrease' in rank):
                template.add_slot(idx, LiteralSlot("decreased"))
            elif slot.fact.what > 0:
                template.add_slot(idx, LiteralSlot("increased"))
            else:
                self._update_slot_value(slot, "stayed the same")
                # Clear the value slot
                self._update_slot_value(what_slot, "")
                return added_slots
            added_slots += 1
            idx += 1

        # Jump over the what_slot
        idx += 1

        # The base unit
        if rank:
            # rikosten määrä kasvoi viidenneksi eniten
            new_slots = self._unit_rank(slot)
        else:
            template.add_slot(idx - 1, LiteralSlot("by"))
            added_slots += 1
            idx += 1
            if percentage:
                # the number of crimes increased by five percent
                new_slots = self._unit_percentage_points(slot)
            else:
                # rikosten määrä kasvoi viidellä
                slot.value = lambda x: ""
                new_slots = 0
        added_slots += new_slots
        idx += new_slots + 1

        # The end comparison
        if grouped_by and 'no_grouping' not in slot.attributes.keys():
            if grouped_by == '_time_place':
                template.add_slot(idx, LiteralSlot("compared to other harmonised indices"))
                added_slots += 1
                idx += 1
            elif grouped_by == '_cphi_time':
                template.add_slot(idx, LiteralSlot("among all harmoniced indices"))
                added_slots += 1
                idx += 1
            elif grouped_by == 'cphi_place_year':
                if slot.fact.when_type == 'month':
                    template.add_slot(idx, LiteralSlot("compared to other months"))
                else:
                    raise AttributeError("This is impossible. _crime_place_year is a valid grouping only for monthly data!")
                added_slots += 1
                idx += 1
            else:
                raise AttributeError("This is impossible. The regex accepts only the above options for this group.")

        return added_slots

    def _unit_rank(self, slot):
        match = self.value_type_re.fullmatch(slot.value)
        unit, normalized, trend, percentage, change, grouped_by, rank = match.groups()
        template = slot.parent
        idx = template.components.index(slot)
        added_slots = 0
        prev_slot = template.components[idx - 1]
        unit = unit.split('_')
        # Add stuff _before_ the what slot ...
        idx -= 1
        if not change:
            if len(unit) > 1:
                new_value = INDICATORS.get(unit[1], unit[1])
            else:
                new_value = INDICATORS.get(unit[0], unit[0])
            template.add_slot(idx, LiteralSlot("HICP value for"))
            idx += 1
            template.add_slot(idx, LiteralSlot(new_value))
            idx += 1
            template.add_slot(idx, LiteralSlot("was"))
            idx += 1
            added_slots += 3

        # Add a definite article before the what slot
        template.add_slot(idx, LiteralSlot("the"))
        added_slots += 1
        idx += 1

        # ... and jump back to the correct index
        idx += 1

        if prev_slot.slot_type == 'what':
            # If the rank is first, the actual numeral isn't realized at all
            if slot.fact.what == 1:
                prev_slot.value = lambda x: ""
            # If the numeral is realized, it needs to be an ordinal
            else:
                prev_slot.value = lambda x: self._ordinal(prev_slot.fact.what)

        if rank in ['_rank', '_increase_rank', '_decrease_rank']:
            slot.value = lambda x: "highest"
        elif rank == '_rank_reverse':
            slot.value = lambda x: "lowest"
        else:
            raise AttributeError("This is impossible. The regex accepts only the above options for this group.")
        idx += 1
        # If talking about changes, we will do the rest in the change handler
        if change:
            return added_slots

        if not change:
            # Skip over the time slot
            idx += 1

            if grouped_by == '_time_place':
                template.add_slot(idx, LiteralSlot("compared to other ???"))
            elif grouped_by == '_cphi_time':
                template.add_slot(idx, LiteralSlot("compared to other price categories"))
            elif grouped_by == '_cphi_place_year':
                if slot.fact.when_type == 'month':
                    template.add_slot(idx, LiteralSlot("compared to other months during the same year"))
                else:
                    raise AttributeError("This is impossible. _crime_place_year is a valid grouping only for monthly data!")
            else:
                raise AttributeError("This is impossible. The regex accepts only the above options for this group.")
            added_slots += 1
            idx += 1

        return added_slots

    def _unit_trend(self, slot):
        match = self.value_type_re.fullmatch(slot.value)
        unit, normalized, trend, percentage, change, grouped_by, rank = match.groups()
        template = slot.parent
        idx = template.components.index(slot)
        added_slots = 0
        what_slot = template.components[idx - 1]
        if what_slot.slot_type != 'what':
            raise AttributeError("The slot before a trend what_type should be the what slot!")

        # Realise the unit of the trend
        crime_name = CRIME_TYPES.get(unit, unit)
        self._update_slot_value(slot, crime_name)
        template.components[0].attributes['focus_slot'] = False
        template.move_slot(idx, 0)
        template.add_slot(0, LiteralSlot("the amount of"))
        added_slots += 1
        idx += 1

        # Realise the direction of the trend
        if what_slot.fact.what < 0:
            self._update_slot_value(what_slot, "decreased")
        elif what_slot.fact.what > 0:
            self._update_slot_value(what_slot, "grew")
        else:
            self._update_slot_value(what_slot, "stayed the same")

        return added_slots

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
        log.info(slot.slot_type)
        if slot.slot_type[:-2] == 'when':
            year, month = slot.value.split("M")
            log.info("Year is {} and month is {}".format(year, month))
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
            slot.attributes['focus_slot'] = True
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
        idx += 1
        if slot.attributes.get('focus_slot', False):
            template.add_slot(idx, LiteralSlot(","))
            added_slots += 1
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
            slot.attributes['focus_slot'] = True
        # The latter condition makes the system realize the full year roughly once in five sentences even
        # if the year hasn't changed.
        if (slot.attributes['name_type'] in ['full', 'short']) or (
                slot.attributes['name_type'] == 'pronoun' and random.rand() > 0.8):
            template.add_slot(idx, LiteralSlot("in"))
            added_slots += 1
            idx += 1
            if slot.attributes['name_type'] == 'full':
                new_slot = LiteralSlot("the year")
                template.add_slot(idx, new_slot)
                added_slots += 1
                idx += 1
            if year is None:
                # We have no idea when the event happened. This shouldn't be possible.
                self._update_slot_value(slot, "unknown")
            elif type(year) is not str:
                self._update_slot_value(slot, self._cardinal(year))
            else:
                self._update_slot_value(slot, year)
        elif slot.attributes['name_type'] == 'pronoun':
            reference_options = ["in the same year", "also during the same year", "also"]
            self._update_slot_value(slot, random.choice(reference_options))
        else:
            raise AttributeError("This is impossible. If we end up here, something is wrong (or has been changed carelessly) elsewhere in the code.")
        idx += 1
        if slot.attributes.get('focus_slot', False):
            template.add_slot(idx, LiteralSlot(","))
            added_slots += 1
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
        template = slot.parent
        idx = template.components.index(slot)
        added_slots = 0
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
        idx += 1
        if slot.value and slot.attributes.get('focus_slot', False):
            template.add_slot(idx, LiteralSlot(","))
            added_slots += 1
        return added_slots
