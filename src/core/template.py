import logging

from templates.substitutions import LiteralSource
from .document_plan import DocumentPlan
log = logging.getLogger('root')


class Template(DocumentPlan):
    """
    A template consisting of TemplateComponent elements and a list of rules about the facts that can be presented
    using the template.
    """

    def __init__(self, components, rules=[], slot_map=None):
        self._rules = rules
        self._facts = []
        self._slot_map = slot_map
        if self._slot_map is None:
            self._slot_map = {}
        self._components = components
        for c in self._components:
            c.parent = self

        self._expresses_location = None
        self._slots = None

    def get_slot(self, slot_type):
        """
        First version of the slot_map: here we are making an assumption that there is only one instance per slot type,
        which is clearly not true after aggregation. Whether this will be a problem is still a bit unclear.

        :param slot_type:
        :return:
        """
        if slot_type not in self._slot_map.keys():
            for slot in self.slots:
                if slot.slot_type == slot_type:
                    self._slot_map[slot_type] = slot
                    break
            else:
                self._slot_map[slot_type] = None
        if self._slot_map[slot_type] is None:
            raise KeyError
        return self._slot_map[slot_type]

    def add_component(self, idx, slot):
        if len(self._components) > idx:
            self._components.insert(idx, slot)
        else:
            self._components.append(slot)
        slot.parent = self
        self.slots.append(slot)


    @property
    def components(self):
        return self._components

    @property
    def children(self):
        return self._components

    @property
    def facts(self):
        return self._facts

    def check(self, primary_message, all_messages, fill_slots=False):
        """
        Like fill(), but doesn't modify the template data structure, just checks whether the given message,
        with the support from other messages, is compatible with the template.

        :param primary_message: The message that the first rule in the template should match
        :param all_messages: A list of other available messages
        :return: True, if the template can be used for the primary_message. False otherwise.
        """
        # ToDo: Could we somehow cache the information about which messages to use in addition to the primary, so that we could then fill the message straight away without going through the messages again?
        # OR: Fill the templates in this phase and then just choose one of them. Filling shouldn't be that much slower than checking.
        primary_fact = primary_message.fact

        used_facts = []

        # The first rule has to match the primary message
        if not all(matcher(primary_fact, used_facts) for matcher in self._rules[0][0]):
            return []
        if fill_slots:
            for slot_index in self._rules[0][1]:
                self._components[slot_index].fact = primary_fact
        used_facts.append(primary_fact)
        # Check the other rules
        if len(self._rules) > 1:
            for (matchers, slot_indexes) in self._rules[1:]:
                # Try each message in turn
                for mess in all_messages:
                    if all(matcher(mess.fact, used_facts) for matcher in matchers):
                        # Found a suitable message: fill the slots
                        if fill_slots:
                            for slot_index in slot_indexes:
                                self._components[slot_index].fact = mess.fact
                        if mess.fact not in used_facts:
                            used_facts.append(mess.fact)
                        # Move onto the next rule
                        break
                else:
                    # No available message matched the rule: we can't use this template:
                    return []
        if fill_slots:
            self._facts = used_facts
        return used_facts

    def fill(self, primary_message, all_messages):
        """
        Search for messages needed to fulfill all of the rules in the template, and link the Slot components to the
        matching Facts

        :param primary_message: The message that the first rule in the template should match
        :param all_messages: A list of other available messages
        :return: A list of the Facts that match the rules in the template
        """

        return self.check(primary_message, all_messages, fill_slots=True)

    @property
    def slots(self):
        # Cache the list of slots to avoid doing too many ifinstance checks
        # The slots are not guaranteed to be in the same order as they appear in the self._components
        if self._slots is None:
            self._slots = [c for c in self.components if isinstance(c, Slot)]
        return self._slots

    @property
    def expresses_location(self):
        """ Whether this template expresses the location (where field) of any of its messages
        """
        if self._expresses_location is None:
            # Check each slot to see whether it expresses a where field
            for slot in self.slots:
                if slot.slot_type in ["where_1", "where_2"]:
                    self._expresses_location = True
                    break
            else:
                # No location field found: we assume the location is not expressed
                self._expresses_location = False
        return self._expresses_location

    def copy(self):
        """Makes a deep copy of this Template. The copy does not contain any messages."""
        component_copy = [c.copy() for c in self.components]
        return Template(component_copy, self._rules)

    def __str__(self):
        return "<Template: n_components={}>".format(len(self.components))

    def display_template(self):
        """String representation of whole template, mainly for debugging"""
        return "".join(str(c) for c in self.components)


class TemplateComponent(object):
    """An abstract TemplateComponent. Should not be used directly."""

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    def __str__(self):
        return str(self.value)


class Slot(TemplateComponent):
    """
    A TemplateComponent that can be filled by a Fact that fulfills a set of
    requirements.
    """

    def __init__(self, to_value, attributes=None):
        """
        :param to_value: A callable that defines how to transform the message
            that fills this slot into a textual representation.
        """

        self.attributes = attributes or {}
        self._to_value = to_value
        self._fact = None
        self._slot_type = self._to_value.field_name

    @property
    def slot_type(self):
        return self._slot_type

    @property
    def fact(self):
        return self._fact

    @fact.setter
    def fact(self, new_fact):
        self._fact = new_fact

    @property
    def value(self):
        return self._to_value(self._fact)

    @value.setter
    def value(self, f):
        self._to_value = f

    def copy(self):
        return Slot(self._to_value, self.attributes.copy())

    def __str__(self):
        return "Slot({}{})".format(
            self.value,
            "".join(", {}={}".format(k, v) for (k, v) in self.attributes.items())
        )


class LiteralSlot(Slot):
    def __init__(self, value, attributes=None):

        self.attributes = attributes or {}
        self._to_value = LiteralSource(value)
        self._fact = None
        self._slot_type = "Literal"

    @property
    def slot_type(self):
        return self._slot_type

    @property
    def fact(self):
        return self._fact

    @fact.setter
    def fact(self, new_fact):
        self._fact = new_fact

    @property
    def value(self):
        return self._to_value(self._fact)

    @value.setter
    def value(self, f):
        self._to_value = f

    def copy(self):
        return Slot(self._to_value, self.attributes.copy())

    def __str__(self):
        return "Slot({}{})".format(
            self.value,
            "".join(", {}={}".format(k, v) for (k, v) in self.attributes.items())
        )


class Literal(TemplateComponent):
    """A string literal."""
    def __init__(self, string):
        self._string = string

    @property
    def slot_type(self):
        return 'Literal'

    @property
    def value(self):
        return self._string

    def copy(self):
        return Literal(self.value)

    def __str__(self):
        return self.value


class DefaultTemplate(Template):

    def __init__(self, message):
        super().__init__(components=[Literal(message)])
