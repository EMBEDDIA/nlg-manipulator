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


class WhereValue(SlotSource):
    """
    Special type of SlotSource for where values.

    """
    # ToDo: replace this with an ordinary FactFieldSource and do the Entity marking elsewhere
    def __init__(self, field_name):
        self.field_name = field_name

    def __call__(self, message):
        return "[ENTITY:{}:{}]".format(getattr(message, 'where_type' + self.field_name[-2:]), getattr(message, self.field_name))

    def __str__(self):
        return "fact.{}".format(self.field_name)
