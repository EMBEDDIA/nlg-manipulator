import re
import logging
from dictionary_en import MONTHS, SMALL_CARDINALS, SMALL_ORDINALS, CPHI, INCOME, HEALTH, COMPARISONS, COUNTRIES, TEMPLATES, PLACES, YEARS

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
            'rank': self._unit_rank,
        }

        self.time = {
            'month': self._time_month,
            'year': self._time_year,
            'month_change': self._time_change_month,
            'year_change': self._time_change_year
        }

    def _unit_base(self, slot):
        template = slot.parent
        idx = template.components.index(slot)
        added_slots = 0
        what_type = slot.fact.what_type.split('_')

        templ = TEMPLATES.get(what_type[0])
        if what_type[0] == 'cphi':
            dictionary = CPHI
        elif what_type[0] == 'income':
            dictionary = INCOME
        elif what_type[0] == 'health':
            dictionary = HEALTH
            
        for t in templ:
            if isinstance(t,int):
                template.add_slot(idx - 1, LiteralSlot(dictionary.get(what_type[t])))
            else:
                template.add_slot(idx - 1, LiteralSlot(t))
            added_slots += 1
            idx += 1 

        self._update_slot_value(slot, '')
        idx += 1            

        if "comp" in slot.fact.what_type:
            template, added_slots, idx = self._comparisons(slot, template, what_type, added_slots, idx)

        return added_slots

    def _comparisons(self, slot, template, what_type, added_slots, idx):
        if slot.fact.what < 0:
            template.add_slot(idx-1, LiteralSlot(COMPARISONS.get('less')))
            added_slots += 1
            idx += 1
        else:
            template.add_slot(idx-1, LiteralSlot(COMPARISONS.get('more')))
            added_slots += 1
            idx += 1
        if "eu" in what_type:
            template.add_slot(idx-1, LiteralSlot(COMPARISONS.get('eu')))
            added_slots += 1
            idx += 1
        elif "us" in what_type:
            template.add_slot(idx-1, LiteralSlot(COMPARISONS.get('us')))
            added_slots += 1
            idx += 1
        elif "similar" in what_type:
            template.add_slot(idx-1, LiteralSlot(COMPARISONS.get('similar')))
            added_slots += 1
            idx += 1
        return template, added_slots, idx        
        

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

        templ = TEMPLATES.get(unit[0])
        if unit[0] == 'cphi':
            dictionary = CPHI
        elif unit[0] == 'income':
            dictionary = INCOME
        elif unit[0] == 'health':
            dictionary = HEALTH

        for t in templ:
            if isinstance(t,int):
                template.add_slot(idx - 1, LiteralSlot(dictionary.get(unit[t])))
            else:
                template.add_slot(idx - 1, LiteralSlot(t))
            added_slots += 1
            idx += 1 

        idx, added_slots, template = self._rank(idx, added_slots, template, slot, prev_slot, rank)

        # If talking about changes, we will do the rest in the change handler
        if change:
            return added_slots
        if not change:
            # Skip over the time slot
            idx += 1

            if grouped_by == '_time':
                template.add_slot(idx, LiteralSlot(COMPARISONS.get('rank')))
            else:   
                raise AttributeError("This is impossible. The regex accepts only the above options for this group.")
            added_slots += 1
            idx += 1

        return added_slots


    def _rank(self, idx, added_slots, template, slot, prev_slot, rank):
        # TODO took of the definite article to combine English and Finnish realization
        # # Add a definite article before the what slot
        # template.add_slot(idx, LiteralSlot("the"))
        # added_slots += 1
        # idx += 1

        # ... and jump back to the correct index
        idx += 1

        if prev_slot.slot_type == 'what':
            # If the rank is first, the actual numeral isn't realized at all
            if slot.fact.what == 1:
                prev_slot.value = lambda x: ""
            # If the numeral is realized, it needs to be an ordinal
            else:
                prev_slot.value = lambda x: self._ordinal(prev_slot.fact.what)

        if rank in ['_rank']:
            slot.value = lambda x: COMPARISONS.get('highest')
        elif rank == '_rank_reverse':
            slot.value = lambda x: COMPARISONS.get('lowest')
        else:
            raise AttributeError("This is impossible. The regex accepts only the above options for this group.")
        idx += 1

        return idx, added_slots, template

    
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
            self._update_slot_value(slot, TEMPLATES.get('month_ssa').format(MONTHS.get(month), year))
        elif slot.attributes['name_type'] == 'pronoun':
            reference_options = MONTHS.get(reference_options)
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
            self._update_slot_value(slot, TEMPLATES.get('year_ssa').format(year))
            if year is None:
                # We have no idea when the event happened. This shouldn't be possible.
                self._update_slot_value(slot, "unknown")
            elif type(year) is not str:
                self._update_slot_value(slot, self._cardinal(year))
            # else:
            #     self._update_slot_value(slot, year)
        elif slot.attributes['name_type'] == 'pronoun':
            reference_options = YEARS.get('reference_options')
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
        if place_type == 'C':
            place = COUNTRIES.get(place)
        if place_type in ["C", "M"]:
            if slot.attributes['name_type'] == 'full':
                self._update_slot_value(slot, prep + place)
            elif random.rand() < 0.5:
                try:
                    self._update_slot_value(slot, prep + PLACES.get(place_type))
                except:
                    raise Exception(
                        "This is impossible. If we end up here, something is wrong (or has been changed carelessly) elsewhere in the code.")
            else:
                self._update_slot_value(slot, "")
        idx += 1
        if slot.value and slot.attributes.get('focus_slot', False):
            template.add_slot(idx, LiteralSlot(","))
            added_slots += 1
        return added_slots
