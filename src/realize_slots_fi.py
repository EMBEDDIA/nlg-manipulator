import re
import logging
from core.template import LiteralSlot
from dictionary_fi import CRIME_TYPES, MONTHS, SMALL_CARDINALS, SMALL_ORDINALS
log = logging.getLogger('root')


class FinnishRealizer():

    value_type_re = re.compile(r'([0-9_a-z]+?)(_normalized)?(?:(_mk_score|_mk_trend)|(_percentage)?(_change)?(?:(?:_grouped_by)(_time_place|_crime_time|_crime_place_year))?((?:_decrease|_increase)?_rank(?:_reverse)?)?)')

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

    def _update_slot_value(self, slot, new_value):
        slot.value = lambda x: new_value
        return 0

    def _unit_set_value(self, slot, new_value):
        slot.value = lambda x: new_value
        case = slot.attributes.get('case', 'nominative')
        # This will try to make necessary case adjustments depending on the value associated with the unit
        self._unit_set_case(slot, case)
        return 0

    def _unit_base(self, slot):
        match = self.value_type_re.fullmatch(slot.value)
        unit, normalized, trend, percentage, change, grouped_by, rank = match.groups()
        template = slot.parent
        idx = template.components.index(slot)
        added_slots = 0

        # Realise the crime type
        content = CRIME_TYPES.get(unit, {}).get('sg', unit)
        try:
            unit, non_case_idx = content
            words = unit.split()
        except ValueError:
            words = content.split()
        if len(words) == 1:
            added = self._unit_set_value(slot, words[0])
        else:
            self._unit_set_value(slot, "")
            case = slot.attributes.get('case', 'nominative')
            added = self._add_slots(template, idx, content, case)
        added_slots += added
        idx += added + 1

        # If we are talking about a normalized value, realise the information about that.
        if normalized:
            template.add_slot(idx, LiteralSlot("1000 asukasta kohti"))
            added_slots += 1
            idx += 1
        return added_slots

    def _unit_percentage(self, slot):
        # Todo: check this, especially cases
        match = self.value_type_re.fullmatch(slot.value)
        unit, normalized, trend, percentage, change, grouped_by, rank = match.groups()
        template = slot.parent
        idx = template.components.index(slot)
        added_slots = 0
        self._unit_set_value(slot, "prosentti")
        idx += 1
        if slot.attributes.get('form') == 'short':
            return added_slots
        added = self._add_slots(template, idx, CRIME_TYPES.get(unit, {}).get('pl', unit), case='elative')
        idx += added
        added_slots += added
        return added_slots

    def _unit_change(self, slot):
        match = self.value_type_re.fullmatch(slot.value)
        unit, normalized, trend, percentage, change, grouped_by, rank = match.groups()
        template = slot.parent
        idx = template.components.index(slot)
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
                self._update_slot_value(slot, "ei muutosta")
                try:
                    slot.attributes.pop('case')
                except KeyError:
                    pass
            else:
                self._update_slot_value(slot, "tapaus")
                idx += 1
                if slot.fact.what < 0:
                    template.add_slot(idx, LiteralSlot("vähemmän"))
                else:
                    template.add_slot(idx, LiteralSlot("enemmän"))
                idx += 1
                added_slots += 1
                if normalized:
                    template.add_slot(idx, LiteralSlot("1000 asukasta kohden"))
                    idx += 1
                    added_slots += 1
            return added_slots

        # The beginning of the full form realisation
        # Move the idx pointer back to add slots before the numerical value
        idx -= 1
        added = self._add_slots(template, idx, CRIME_TYPES.get(unit, {}).get('pl', unit), case='genitive')
        idx += added
        added_slots += added

        template.add_slot(idx, LiteralSlot("määrä"))
        added_slots += 1
        idx += 1

        # Specify the normalisation if needed
        if normalized and 'no_normalization' not in slot.attributes.keys():
            if rank or percentage:
                # with rank or percentage values we don't need to specify the exact normalizing factor
                template.add_slot(idx, LiteralSlot("suhteessa asukaslukuun"))
            else:
                # absolute normalized values don't make sense without this information
                template.add_slot(idx, LiteralSlot("1000 asukasta kohden"))
            added_slots += 1
            idx += 1

        # Specify the predicate
        if 'no_normalization' not in slot.attributes.keys():
            if slot.fact.what < 0 or (rank and ('_decrease' in rank or '_reverse' in rank)):
                template.add_slot(idx, LiteralSlot("laski"))
            elif slot.fact.what > 0:
                template.add_slot(idx, LiteralSlot("kasvoi"))
            else:
                self._update_slot_value(slot, "säilyi ennallaan")
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
            new_slots = self._unit_rank(slot, comp='no_normalization' not in slot.attributes.keys())
            added_slots += new_slots
        elif percentage:
            # rikosten määrä kasvoi viidellä prosenttiyksiköllä
            slot.attributes['case'] = 'adessive'
            what_slot.attributes['case'] = 'adessive'
            new_slots = self._unit_set_value(slot, "prosenttiyksikkö")
            added_slots += new_slots
        else:
            # rikosten määrä kasvoi viidellä
            what_slot.attributes['case'] = 'adessive'
            slot.value = lambda x: ""
        idx += 1

        # The end comparison
        if grouped_by and 'no_grouping' not in slot.attributes.keys():
            if grouped_by == '_time_place':
                template.add_slot(idx, LiteralSlot("muihin rikostyyppeihin verrattuna"))
                added_slots += 1
                idx += 1
            elif grouped_by == '_crime_time':
                template.add_slot(idx, LiteralSlot("kaikista Suomen kunnista"))
                added_slots += 1
                idx += 1
            elif grouped_by == 'crime_place_year':
                if slot.fact.when_type == 'month':
                    template.add_slot(idx, LiteralSlot("muihin kuukausiin verrattuna"))
                else:
                    raise AttributeError("This is impossible. _crime_place_year is a valid grouping only for monthly data!")
                added_slots += 1
                idx += 1
            else:
                raise AttributeError("This is impossible. The regex accepts only the above options for this group.")
        return added_slots

    def _unit_rank(self, slot, comp=False):
        match = self.value_type_re.fullmatch(slot.value)
        unit, normalized, trend, percentage, change, grouped_by, rank = match.groups()
        template = slot.parent
        idx = template.components.index(slot)
        added_slots = 0
        prev_slot = template.components[idx - 1]
        if not change:
            if grouped_by == '_time_place':
                template.add_slot(idx - 1, LiteralSlot("kaikista rikoksista"))
            elif grouped_by == '_crime_time':
                template.add_slot(idx - 1, LiteralSlot("kaikista Suomen kunnista"))
            elif grouped_by == '_crime_place_year':
                if slot.fact.when_type == 'month':
                    template.add_slot(idx - 1, LiteralSlot("vuoden muihin kuukausiin verrattuna"))
                else:
                    raise AttributeError("This is impossible. _crime_place_year is a valid grouping only for monthly data!")
            else:
                raise AttributeError("This is impossible. The regex accepts only the above options for this group.")
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
        if rank in ['_rank', '_increase_rank', '_decrease_rank'] or comp:
            slot.value = lambda x: "eniten"
        elif rank == '_rank_reverse':
            slot.value = lambda x: "vähiten"
        else:
            raise AttributeError("This is impossible. The regex accepts only the above options for this group.")
        idx += 1
        # If talking about changes, we will do the rest in the change handler
        if change:
            return added_slots
        added = self._add_slots(template, idx, CRIME_TYPES.get(unit, {}).get('pl', unit), case='partitive')
        idx += added
        added_slots += added
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
        content = CRIME_TYPES.get(unit, {}).get('pl', unit)
        try:
            unit, non_case_idx = content
            words = unit.split()
        except ValueError:
            words = content.split()
        if len(words) == 1:
            added = self._unit_set_value(slot, words[0])
            slot.attributes['case'] = 'genitive'
            template.move_slot(idx, 0)
            template.add_slot(1, LiteralSlot("määrä"))
        else:
            self._unit_set_value(slot, "")
            added = self._add_slots(template, 0, content, 'genitive')
            template.add_slot(added, LiteralSlot("määrä"))
        added_slots += added + 1
        idx += added + 1

        # Realise the direction of the trend
        if what_slot.fact.what < 0:
            self._update_slot_value(what_slot, "laski")
        elif what_slot.fact.what > 0:
            self._update_slot_value(what_slot, "kasvoi")
        else:
            self._update_slot_value(what_slot, "pysyi ennallaan")

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
                template.add_slot(idx + added_slots, new_slot)
                added_slots += 1
        # If the content doesn't contain a list of indexes, assume that all words in it should be inflected:
        except ValueError:
            words = content.split()
            for word in words:
                new_slot = LiteralSlot(word)
                if case:
                    new_slot.attributes['case'] = case
                template.add_slot(idx + added_slots, new_slot)
                added_slots += 1
        return added_slots

    def _unit_set_case(self, slot, case):
        if case == 'nominative':
            self._unit_set_nominative(slot)
        elif case == 'accusative':
            self._unit_set_accusative(slot)
        else:
            slot.attributes['case'] = case

    def _unit_set_nominative(self, slot):
        """
        Set the case for the unit slot to the proper case for a nominative form.
        This is nominative when the value corresponding to the unit is 1, and partitive otherwise.
        :param slot:
        :return:
        """
        prev_slot = slot.parent.components[slot.parent.components.index(slot) - 1]
        # "yksi/-1 rikos"
        if abs(slot.fact.what) == 1:
            slot.attributes['case'] = 'nominative'
        # "nolla/kaksi/1,25 rikosta"
        else:
            slot.attributes['case'] = 'partitive'

    def _unit_set_accusative(self, slot):
        """
        Set the cases for the slot (and the previous slot, if it contains a value) to the proper case for accusative.
        This is genitive for both when the value is 1, and nominative for the numeral and partitive for the unit
        otherwise.
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
                if 'case' in slot.attributes.keys():
                    new_slot = LiteralSlot("vuosi")
                    new_slot.attributes['case'] = slot.attributes['case']
                    slot.attributes['case'] = 'nominative'
                else:
                    new_slot = LiteralSlot("vuonna")
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
            reference_options = ["samana vuonna", "tuolloin myös", "myös"]
            self._update_slot_value(slot, random.choice(reference_options))
        else:
            raise AttributeError("This is impossible. If we end up here, something is wrong (or has been changed carelessly) elsewhere in the code.")
        return added_slots

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
            new_slot = LiteralSlot(MONTHS[month])
            new_slot.attributes['case'] = 'inessive'
            template.add_slot(idx, new_slot)
            added_slots += 1
            idx += 1
            self._update_slot_value(slot, year)
        elif slot.attributes['name_type'] == 'pronoun':
            reference_options = ["samassa kuussa", "tuolloin myös", "myös", "samaan aikaan"]
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
            if 'case' in slot.attributes.keys():
                new_slot = LiteralSlot("aikaväli")
                new_slot.attributes['case'] = slot.attributes['case']
                template.add_slot(idx, new_slot)
                added_slots += 1
                idx += 1
                self._update_slot_value(slot, match.group(1) + "-" + match.group(2))
                slot.attributes['case'] = 'nominative'
            else:
                new_slot = LiteralSlot("vuosi")
                new_slot.attributes['case'] = 'elative'
                template.add_slot(idx, new_slot)
                added_slots += 1
                idx += 1
                template.add_slot(idx, LiteralSlot(match.group(1)))
                added_slots += 1
                idx += 1
                new_slot = LiteralSlot("vuosi")
                new_slot.attributes['case'] = 'illative'
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
            if 'case' in slot.attributes.keys():
                new_slot = LiteralSlot("aikaväli")
                new_slot.attributes['case'] = slot.attributes['case']
                template.add_slot(idx, new_slot)
                added_slots += 1
                idx += 1
                self._update_slot_value(slot, month1 + "/" + year1 + "-" + month2 + "/" + year2)
                slot.attributes['case'] = 'nominative'
            else:
                new_slot = LiteralSlot(MONTHS[month1])
                new_slot.attributes['case'] = 'elative'
                template.add_slot(idx, new_slot)
                added_slots += 1
                idx += 1
                template.add_slot(idx, LiteralSlot(year1))
                added_slots += 1
                idx += 1
                new_slot = LiteralSlot(MONTHS[month2])
                new_slot.attributes['case'] = 'illative'
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
        if place_type == 'C' and place == 'fi':
            place = "Suomi"
        if place_type in ["C", "M"]:
            if slot.attributes['name_type'] == 'full':
                self._update_slot_value(slot, place)
            elif random.rand() < 0.5:
                if place_type == 'M':
                    self._update_slot_value(slot, "paikkakunta")
                elif place_type == 'C':
                    self._update_slot_value(slot, "maa")
                else:
                    raise Exception(
                        "This is impossible. If we end up here, something is wrong (or has been changed carelessly) elsewhere in the code.")
            else:
                self._update_slot_value(slot, "")
        return 0
