
def canonical_map(map_dict):
    return dict(
        (alt_val, canonical) for (canonical, alt_vals) in map_dict.items() for alt_val in ([canonical] + alt_vals)
    )


# Defines alternative, equivalent field names for use in templates
# The alternatives get mapped to their canonical form (key) early in processing
FACT_FIELD_ALIASES = {
    "what_type_1": [],
    "what_type_2": ["value_type", "unit"],
    "what_1": [],
    "what_2": ["value"],
    "who_type_1": [],
    "who_type_2": ["name_type"],
    "who_1": [],
    "who_2": ["name"],
    "where_type_1": [],
    "where_type_2": ["place_type"],
    "where_1": [],
    "where_2": ["place"],
    "when_1": [],
    "when_2": ["time"],
}
FACT_FIELD_MAP = canonical_map(FACT_FIELD_ALIASES)

# This defines alternative values for name types
# Currently there aren't any, but we define the mapping for consistency, in case we want to add some later
NAME_TYPES = {
    "candidate": [],
    "party": [],
}
NAME_TYPE_MAP = canonical_map(NAME_TYPES)


# Similarly, we have multiple ways to refer to location types
LOCATION_TYPES = {
    "C": ["country"],
    "D": ["district"],
    "M": ["municipality", "mun"],
    "P": ["polling_station", "pollingstation"]
}
LOCATION_TYPE_MAP = canonical_map(LOCATION_TYPES)


FACT_FIELDS = FACT_FIELD_ALIASES.keys()
