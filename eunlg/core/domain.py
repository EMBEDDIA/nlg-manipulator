import operator
import re
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Tuple, Union, cast


class Fact(NamedTuple):
    where: Any
    where_type: str
    what: Any
    what_type: str
    when_1: Any
    when_2: Any
    when_type: str
    outlierness: float


class Message:
    """
    Contains a list of Fact tuples, a template for presenting the facts, and various values that are computed based on
    the facts.

    _importance_coefficient: scales the importance of the message, allowing less relevant messages to be included in the
    article only if their importance is high enough to outweigh having a lower coefficient
    _polarity: tells whether the message is considered positive, neutral or negative. For now the value is -1, 0, or 1.
    _score: is the newsworthiness score, that is used to decide which messages to include in the news article
    _template: is a Template object that contains information on how to display the message

    """

    def __init__(
        self,
        facts: Union[List[Fact], Fact],
        importance_coefficient: float = 1.0,
        score: float = 0.0,
        polarity: float = 0.0,
    ) -> None:
        self.facts: List[Fact] = facts if isinstance(facts, list) else [facts]
        self.template: Optional[Template] = None
        self.importance_coefficient: float = importance_coefficient
        self.score: float = score
        self.polarity: float = polarity
        self._main_fact: Fact = self.facts[0]
        self.prevent_aggregation: bool = False

    # Added for backwards compatibility, returns by default the primary fact for this Message.
    @property
    def fact(self) -> Fact:
        return self._main_fact

    @fact.setter
    def fact(self, new_fact: Fact) -> None:
        self._main_fact = new_fact

    # This is kind of ugly, and should be gotten rid of later, for now it's needed for some of the recursions to
    # work properly
    @property
    def children(self) -> List["Template"]:
        return [self.template]

    @property
    def components(self) -> List["TemplateComponent"]:
        if self.template is None:
            return []
        else:
            return self.template.components

    def __str__(self) -> str:
        return "<Message>"


def equal_op(a: Any, b: Any) -> bool:
    if type(b) is str:
        return re.match("^" + b + "$", str(a)) is not None
    else:
        return operator.eq(a, b)


OPERATORS = {
    "=": equal_op,
    "!=": operator.ne,
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
    "in": lambda a, b: operator.contains(b, a),
}


class Matcher:
    def __init__(
        self,
        lhs: Callable[["Fact", List["Fact"]], Any],
        op: str,
        value: Union[str, Callable[["Fact", List["Fact"]], Any]],
    ):
        if op not in OPERATORS:
            raise ValueError("invalid matcher operator '{}'. Must be one of: {}".format(op, ", ".join(OPERATORS)))
        self.value = value
        self.op = op
        self.lhs = lhs

    def __call__(self, fact: "Fact", all_facts: List["Fact"]) -> bool:
        # Process the LHS expression
        result = self.lhs(fact, all_facts)
        if callable(self.value):
            value = self.value(fact, all_facts)
        else:
            value = self.value
        # Perform the relevant comparison operator
        return OPERATORS[self.op](result, value)

    def __str__(self) -> str:
        return "lambda msg, all: {} {} {}".format(self.lhs, self.op, self.value)

    def __repr__(self) -> str:
        return str(self)


class LhsExpr:
    """Symbolic representation of expressions on the LHS of message constraints.

    We could just represent these expressions using lambda expressions, but this symbolic representation makes
    it easier to view them after they've been read in, to debug template reading, view templates, and so on.

    The __call__ methods perform the actual processing of the message to get a value to compare to the RHS
    of the constraint.

    """

    def __call__(self, fact: "Fact", all_facts: List["Fact"]) -> Any:
        # Required in subclasses
        raise NotImplementedError()

    def __str__(self) -> str:
        # Required in subclasses
        raise NotImplementedError

    def __repr__(self) -> str:
        return str(self)


class FactField(LhsExpr):
    def __init__(self, field_name: str) -> None:
        self.field_name = field_name

    def __call__(self, fact: "Fact", all_facts: List["Fact"]) -> Any:
        return getattr(fact, self.field_name)

    def __str__(self) -> str:
        return "fact.{}".format(self.field_name)


class ReferentialExpr:
    def __init__(self, reference_idx: int, field_name: str) -> None:
        self.field_name = field_name
        self.reference_idx = reference_idx

    def __call__(self, message: "Message", all_messages: List["Message"]) -> Any:
        return getattr(all_messages[self.reference_idx], self.field_name)

    def __str__(self) -> str:
        return "all[{}].{}".format(self.reference_idx, self.field_name)


FACT_FIELD_ALIASES: Dict[str, List[str]] = {
    "what_type": ["value_type", "unit"],
    "what": ["value"],
    "where_type": ["place_type"],
    "where": ["place"],
    "when_1": [],
    "when_2": [],
    "time": [],
    "empty": [],
}


def canonical_map(map_dict: Dict[str, List[str]]) -> Dict[str, str]:
    # TODO: Proper typingUnion
    return dict(
        (alt_val, canonical) for (canonical, alt_vals) in map_dict.items() for alt_val in ([canonical] + alt_vals)
    )


FACT_FIELD_MAP = canonical_map(FACT_FIELD_ALIASES)
FACT_FIELDS = FACT_FIELD_ALIASES.keys()


class Template:
    """
    A template consisting of TemplateComponent elements and a list of rules about the facts that can be presented
    using the template.
    """

    _rules: List[Tuple[List[Matcher], List[int]]]
    _facts: List[Fact]
    _slot_map: Dict[str, Optional["Slot"]]
    _components: List["TemplateComponent"]
    _slots: List["Slot"]
    _expresses_location: Optional[bool]

    def __init__(
        self,
        components: List["TemplateComponent"],
        rules: Optional[List[Tuple[List[Matcher], List[int]]]] = None,
        slot_map: Optional[Dict[str, Optional["Slot"]]] = None,
    ):
        self._rules = rules if rules is not None else []
        self._facts = []
        self._slot_map = slot_map if slot_map is not None else {}
        self._components = components
        for c in self._components:
            c.parent = self

        self._slots = [c for c in components if isinstance(c, Slot)]
        self._expresses_location = None

    def get_slot(self, slot_type: str) -> "Slot":
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

    def add_component(self, idx: int, component: "TemplateComponent") -> None:
        if len(self._components) > idx:
            self._components.insert(idx, component)
        else:
            self._components.append(component)
        component.parent = self
        if isinstance(component, Slot):
            self.slots.append(component)

    def move_component(self, from_idx: int, to_idx: int) -> None:
        if from_idx >= to_idx:
            self.components.insert(to_idx, self.components.pop(from_idx))
        else:
            self.components.insert(to_idx - 1, self.components.pop(from_idx))

    @property
    def components(self) -> List["TemplateComponent"]:
        return self._components

    @property
    def children(self) -> List["TemplateComponent"]:
        return self._components

    @property
    def facts(self) -> List[Fact]:
        return self._facts

    def check(self, primary_message: Message, all_messages: List[Message], fill_slots: bool = False) -> List[Fact]:
        # ToDo: Could we somehow cache the information about which messages to use in addition to the primary, so
        #  that we could then fill the message straight away without going through the messages again?
        # OR: Fill the templates in this phase and then just choose one of them. Filling shouldn't be that much slower t
        # han checking.
        primary_fact = primary_message.fact

        used_facts: List[Fact] = []

        # The first rule has to match the primary message
        if not all(matcher(primary_fact, used_facts) for matcher in self._rules[0][0]):
            return []
        if fill_slots:
            for slot_index in self._rules[0][1]:
                slot = cast("Slot", self.components[slot_index])
                assert isinstance(slot, Slot)
                slot.fact = primary_fact
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
                                slot = cast("Slot", self.components[slot_index])
                                assert isinstance(slot, Slot)
                                slot.fact = mess.fact
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

    def fill(self, primary_message: Message, all_messages: List[Message]) -> List[Fact]:
        """
        Search for messages needed to fulfill all of the rules in the template, and link the Slot components to the
        matching Facts

        :param primary_message: The message that the first rule in the template should match
        :param all_messages: A list of other available messages
        :return: A list of the Facts that match the rules in the template
        """

        return self.check(primary_message, all_messages, fill_slots=True)

    @property
    def slots(self) -> List["Slot"]:
        # Cache the list of slots to avoid doing too many ifinstance checks
        # The slots are not guaranteed to be in the same order as they appear in the self._components
        if self._slots is None:
            self._slots = [c for c in self.components if isinstance(c, Slot)]
        return self._slots

    @property
    def expresses_location(self) -> bool:
        """ Whether this template expresses the location (where field) of any of its messages
        """
        if self._expresses_location is None:
            # Check each slot to see whether it expresses a where field
            for slot in self.slots:
                if slot.slot_type == "where":
                    self._expresses_location = True
                    break
            else:
                # No location field found: we assume the location is not expressed
                self._expresses_location = False
        return self._expresses_location

    def copy(self) -> "Template":
        """Makes a deep copy of this Template. The copy does not contain any messages."""
        component_copy = [c.copy() for c in self.components]
        return Template(component_copy, self._rules)

    def __str__(self):
        return "<Template: n_components={}>".format(len(self.components))

    def display_template(self):
        """String representation of whole template, mainly for debugging"""
        return "".join(str(c) for c in self.components)


class TemplateComponent(ABC):
    """An abstract TemplateComponent. Should not be used directly."""

    parent = None
    value = None

    def __str__(self):
        return str(self.value)

    @abstractmethod
    def copy(self) -> "TemplateComponent":
        ...


class Slot(TemplateComponent):
    """
    A TemplateComponent that can be filled by a Fact that fulfills a set of
    requirements.
    """

    def __init__(
        self, to_value: "SlotSource", attributes: Optional[Dict[str, Any]] = None, fact: Optional[Fact] = None
    ) -> None:
        """
        :param to_value: A callable that defines how to transform the message
            that fills this slot into a textual representation.
        """

        self.attributes = attributes or {}
        self._to_value = to_value
        self.fact = fact

    @property
    def slot_type(self):
        return self._to_value.field_name

    @property
    def value(self):
        return self._to_value(self.fact)

    def add_attribute(self, name: str, value: Any) -> None:
        self.attributes[name] = value

    @value.setter
    def value(self, f: "SlotSource") -> None:
        self._to_value = f

    def copy(self) -> "Slot":
        return Slot(self._to_value, self.attributes.copy())

    def __str__(self) -> str:
        return "Slot({}{})".format(self.value, "".join(", {}={}".format(k, v) for (k, v) in self.attributes.items()))


class LiteralSlot(Slot):
    def __init__(self, value: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(LiteralSource(value), attributes, None)

    @property
    def slot_type(self):
        return "Literal"


class Literal(TemplateComponent):
    """A string literal."""

    def __init__(self, value: str) -> None:
        self.value = value

    @property
    def slot_type(self) -> str:
        return "Literal"

    def copy(self) -> "Literal":
        return Literal(self.value)

    def __str__(self) -> str:
        return self.value


class EmptySlot(Slot):
    def __init__(self, attributes: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(EmptySource("empty"), attributes, None)

    @property
    def slot_type(self):
        return "empty"


class DefaultTemplate(Template):
    def __init__(self, message):
        super().__init__(components=[Literal(message)])


class SlotSource(ABC):
    """ Source of the slot value """

    field_name: str

    @abstractmethod
    def __call__(self, fact: Optional[Fact]) -> Any:
        ...


class FactFieldSource(SlotSource):
    def __init__(self, field_name: str):
        self.field_name = field_name

    def __call__(self, fact: Optional[Fact]) -> Any:
        assert fact is not None
        return getattr(fact, self.field_name)

    def __str__(self) -> str:
        return "fact.{}".format(self.field_name)


class LiteralSource(SlotSource):
    """Ignore the message and return a literal value"""

    def __init__(self, value: str):
        self.value = value

    def __call__(self, fact: Optional[Fact]) -> str:
        return self.value

    def __str__(self) -> str:
        return '"{}"'.format(self.value)


class EntitySource(SlotSource):
    """
    Special type of SlotSource for named entities.
    """

    def __init__(self, field_name: str) -> None:
        self.field_name = field_name

    def __call__(self, fact: Optional[Fact]) -> str:
        assert fact is not None
        return "[PLACE:{}:{}]".format(getattr(fact, self.field_name + "_type"), getattr(fact, self.field_name))

    def __str__(self) -> str:
        return "fact.{}".format(self.field_name)


class TimeSource(SlotSource):
    """
    Special type of SlotSource for time entries.
    """

    def __init__(self, field_name: str) -> None:
        self.field_name = field_name

    def __call__(self, fact: Optional[Fact]) -> str:
        assert fact is not None
        return "[TIME:{}:{}]".format(getattr(fact, "when_1"), getattr(fact, "when_2"))

    def __str__(self):
        return "fact.time"


class EmptySource(SlotSource):
    """
    Special type of SlotSource for empty slots.
    """

    def __init__(self, field_name):
        self.field_name = field_name

    def __call__(self, message):
        return self.field_name

    def __str__(self):
        return '"{}"'.format(self.field_name)
