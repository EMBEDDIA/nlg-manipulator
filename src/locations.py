

class LocationHierarchy(object):
    """
    Indexes geodata in a way that makes it easy to look up locations in the hierarchy and go up and down, etc.

    """
    def __init__(self, geodata):
        self.ids_by_type = {}
        self.parents = {}
        self.index_geodata(geodata)

    def index_geodata(self, geodata):
        # Store pointer to this point in the hierarchy for this type-id combination
        self.ids_by_type.setdefault(geodata["type"], {})[geodata["id"]] = geodata
        # Recurse to index all children
        for child_data in geodata["children"].values():
            self.index_geodata(child_data)
            # Also index a pointer up the hierarchy to each node's parent
            self.parents[(child_data["type"], child_data["id"])] = geodata

    def __getitem__(self, item):
        # Query by (type, id) pair
        loc_type, loc_id = item
        try:
            type_index = self.ids_by_type[loc_type]
        except KeyError:
            raise KeyError("location type '{}' not in index".format(loc_type))
        try:
            return type_index[loc_id]
        except KeyError:
            raise KeyError("location ID '{}' not in index for type '{}'".format(loc_id, loc_type))


# Types corresponding to different levels in the hierarchy
LOCATION_TYPES = ["P", "M", "D", "C"]
# Get the level for a given location type
TYPE_LEVELS = dict((t, level) for (level, t) in enumerate(LOCATION_TYPES))
