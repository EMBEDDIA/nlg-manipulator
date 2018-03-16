
class SlotFilterChain(object):
    """
    In textual specs for templates, processing of fact fields to map to template slot fillers is given
    in the form of a list of filters applied to the field. This can also be thought of as a series of
    embedded function calls (which is how we'd implement them in Python).

    As with fact matchers, we use special classes to represent the filters, instead of just building
    their functionality as Python functions, because it allows us to easily output a description of the
    chain of processing, making it possible to inspect templates after they've been read in.

    """
    def __init__(self, source, filters=None):
        self.source = source
        if filters is None:
            filters = []
        self.filters = filters

    def __call__(self, message):
        """ Apply the whole chain of filtering to a message to get the string value to substitute """
        last_output = self.source(message)
        # Apply to the filters in order
        for f in self.filters:
            last_output = f(last_output, message)
        # The output is not guaranteed to be a string
        return last_output

    def __str__(self):
        if len(self.filters):
            return "{} -> {}".format(self.source, " -> ".join(str(f) for f in self.filters))
        else:
            return str(self.source)


class SlotSource(object):
    """ Source of the value to be passed through filters """
    def __call__(self, message):
        raise NotImplementedError("abstract slot source")


class FactFieldSource(SlotSource):
    def __init__(self, field_name):
        self.field_name = field_name

    def __call__(self, message):
        return getattr(message, self.field_name)

    def __str__(self):
        return "fact.{}".format(self.field_name)


class LiteralSource(SlotSource):
    """Ignore the message and return a literal value"""
    def __init__(self, value):
        self.value = value

    def __call__(self, message):
        return self.value

    def __str__(self):
        return '"{}"'.format(self.value)


class SlotFilter(object):
    name = None

    def __init__(self, **args):
        self.args = args

    def __call__(self, input, original_message):
        raise NotImplementedError("SlotFilter subclass must implement __call__")

    def __str__(self):
        if len(self.args):
            return "{}({})".format(self.name, ", ".join(self.args))
        else:
            return self.name


class AbsFilter(SlotFilter):
    """ Take absolute value of input. Expects input to be a numeric type """
    name = "abs"

    def __call__(self, input, original_message):
        return abs(input)


class PartyFilter(SlotFilter):
    """Identify the slot contents as a party for entity name resolution purposes"""
    name = "as-party"

    def __call__(self, input, original_message):
        return "[ENTITY:party:{}]".format(input)


class WhoValue(SlotFilterChain):
    """
    Special type of filter chain for who values (no filters allowed).

    """
    def __init__(self, field_name):
        super().__init__(FactFieldSource(field_name), filters=[])

    def __call__(self, message):
        return "[ENTITY:{}:{}]".format(message.who_type_2, message.who_2)


class WhereValue(SlotFilterChain):
    """
    Special type of filter chain for where values (no filters allowed).

    """
    def __init__(self, field_name):
        super().__init__(FactFieldSource(field_name), filters=[])

    def __call__(self, message):
        return "[ENTITY:{}:{}]".format(message.where_type_2, message.where_2)


# Use this dict to get the filter class corresponding to a filter name used in a template spec
SLOT_FILTERS = dict((f.name, f) for f in [AbsFilter, PartyFilter])
