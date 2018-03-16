import logging

from core import MessageGenerator, NoMessagesForSelectionException
from locations import TYPE_LEVELS, LOCATION_TYPES

log = logging.getLogger('root')

# Various hand-coded importance coefficients for different types of expansion
IC_SAME_LOC_SAME_WHO_TYPE = 0.3
IC_SAME_LOC_DIFF_WHO_TYPE = 0.2
# Define importance coefficients for going up or down from each level in the location hierarchy
# These are multiplicative: if we go up multiple levels, we multiply the coefficients
LOC_LEVEL_CHANGE_COEFS = {
    0: (0, None),  # Can only go up from polling station
    1: (0, 0),   # M->D quite interesting, M->P must be a really interesting fact to be worth including
    2: (0., 0),   # D->C probably interesting, D->M fairly interesting
    3: (None, 0),  # In article about the country, we're likely to want to include things about districts
}
# Max number of locations lower down the hierarchy that we'll consider in fact expansion
# If a node (e.g. municipality) has too many children, we select this number at random to try finding interesting facts
MAX_LOWER_LOCATIONS = 10
# Max number of records to get messages from for each expanded location (higher or lower in the tree than the query)
# If there are more records available, a random sample is taken
# Note that this is the number of records: there will be lots of messages from each matching record
MAX_EXP_LOCATION_RECORDS = 10


class MunicipalElectionMessageGenerator(MessageGenerator):
    """
    An NLGPipelineComponent that creates messages from MinistryOfJustice election results data.
    """
    def __init__(self, expand=True):
        super(MunicipalElectionMessageGenerator, self).__init__()
        if expand:
            # Prepare a message expander to get related messages in addition to our simple selection
            self.expander = MunicipalElectionMessageExpander()
        else:
            self.expander = None

    def run(self, registry, random, language, who, who_type, where, where_type, when=None, when_type="year"):
        """
        Run this pipeline component.
        """
        messages = []

        log.info("Generating messages from party data")
        datastore = registry.get('moj-results-party')
        ignored_party_fields = [
            "party_name_short_fi",
            "party_name_short_sv",
            "party_name_fi",
            "party_name_sv",
        ]
        party_messages = (super().run(registry, random, language, datastore, who, who_type, where, where_type, when, when_type, ignored_cols=ignored_party_fields))[0]
        if self.expander is not None:
            # Get an expanded set of messages
            exp_party_messages = self.expander.run(registry, random, language, datastore, who, who_type, where, where_type, when, when_type, ignored_cols=ignored_party_fields)[0]
            party_messages.extend(exp_party_messages)
        # Some special filters to deal with quirks in the data, not needed since these should be filtered out in the data import phase
        # party_messages = [msg for msg in party_messages if not (msg.fact.where_type == 'P' and ('seats' in msg.fact.what_type or 'change' in msg.fact.what_type or 'previous' in msg.fact.what_type))]
        messages.extend(party_messages)

        log.info("Generating messages from candidate data")
        datastore = registry.get('moj-results-candidate')
        ignored_candidate_fields = [
            "name",
            "gender",
            "gender_rank"
        ]
        candidate_messages = (super().run(registry, random, language, datastore, who, who_type, where, where_type, when, when_type, ignored_cols=ignored_candidate_fields))[0]

        if self.expander is not None:
            # Get an expanded set of messages
            exp_candidate_messages = self.expander.run(registry, random, language, datastore, who, who_type, where, where_type, when, when_type, ignored_cols=ignored_candidate_fields)[0]
            candidate_messages.extend(exp_candidate_messages)

        # Some special filters to deal with quirks in the data, should not be needed since these should be filtered out earlier
        # candidate_messages = [msg for msg in candidate_messages if not (msg.fact.where_type == 'P' and ('seats' in msg.fact.what_type or 'change' in msg.fact.what_type or 'previous' in msg.fact.what_type))]
        # Remove "X is not Y"
        candidate_messages = [cm for cm in candidate_messages if not (cm.fact.what_type_2.startswith("is_") and cm.fact.what_2 == False)]

        messages.extend(candidate_messages)

        if not messages:
            raise NoMessagesForSelectionException()

        return (messages, )


class MunicipalElectionMessageExpander(MessageGenerator):
    """
    Generates a larger set of messages that don't exactly correspond to the query, but may be related, e.g.
    related regions for the same party, other news from the same location.

    These should be included if they're sufficiently interesting, but the interestingness is more harshly
    scored, since a fact needs to be much more interesting to be worth including if it's not what the user
    queried.

    """

    def run(self, registry, random, language, datastore, who, who_type, where, where_type, when, when_type, ignored_cols=None):
        log.info("Generating expanded message set for who={}, who_type={}, where={}, where_type={}, when={}, when_type={}".format(who, who_type, where, where_type, when, when_type))
        if ignored_cols is None:
            ignored_cols = []

        # Get the location hierarchy index to help with expanding queries to different locations
        geo_index = registry.get('geodata-hierarchy')[language]

        messages = []
        if who is not None and where is not None:
            ### Same place, other candidates/parties ###
            # We had a specific who, but might also be interested in other whos in the same location
            # Whos of the same type (candidate-candidate, party-party) are more interesting than another type
            _imp_coeff = lambda w, mwho_type, wr, wrt, wn, wnt, wt, wtt: IC_SAME_LOC_SAME_WHO_TYPE if mwho_type == who_type \
                else IC_SAME_LOC_DIFF_WHO_TYPE

            new_messages = self.message_query(datastore, where=where, where_type=where_type, when=when, when_type=when_type,
                                              ignored_cols=ignored_cols, importance_coefficient=_imp_coeff)
            # Don't include the exact match of who/who_type, as that should already be in the basic set
            new_messages = [m for m in new_messages if not (m.fact.who_2 == who and m.fact.who_type_2 == who_type)]
            if len(new_messages):
                log.info("Expanded message set by {} by opening up who restriction".format(len(new_messages)))
            messages.extend(new_messages)

        if where is not None and where_type is not None:
            ### Up or down in hierarchy, same candidate/party ###
            # We specified a location, but might also be interested in larger locations containing it, or smaller
            #  ones within it (provided the facts are sufficiently interesting)
            new_up_messages = []
            new_down_messages = []
            # Check what level we're at in the hierarchy
            hierarchy_level = TYPE_LEVELS[where_type]

            # Gather related locations that may be interesting
            node_geodata = geo_index[(where_type, where)]
            if hierarchy_level < 3:
                # Include the ancestors of this node in the tree, right up to country
                change_coef = 1.
                current_node = node_geodata
                for expand_level in range(hierarchy_level+1, 4):
                    # Get the ID of the parent
                    parent_node = geo_index.parents[(current_node["type"], current_node["id"])]
                    # Compute a coefficient for going up this far in the tree, multiplying all the way from the source
                    change_coef *= LOC_LEVEL_CHANGE_COEFS[expand_level-1][0]
                    if change_coef == 0:
                        # Early stop if none of the generated messages will be newsworthy
                        continue

                    # Horrible hack which brings shame upon us and all our families
                    # Helsinki voting district contains only Helsinki municipality, so we don't want to expand facts
                    #  from one to the other
                    if node_geodata["id"] == "91" and node_geodata["type"] == "M":
                        current_node = parent_node
                        continue

                    # Make a query using the parent (or ancestor) location
                    new_up_messages.extend(
                        self.message_query(datastore, who=who, who_type=who_type,
                                           where_type=parent_node["type"], where=parent_node["id"],
                                           when=when, when_type=when_type,
                                           importance_coefficient=change_coef,
                                           limit_records=MAX_EXP_LOCATION_RECORDS, random=random)
                    )
                    current_node = parent_node

            if hierarchy_level > 0 and LOC_LEVEL_CHANGE_COEFS[hierarchy_level][1] > 0:
                # Only go one level down in the hierarchy: include all children
                # Do not do anything if coeffs are quaranteed to be zero

                # Sort the keys to make behaviour consistent
                child_ids = sorted(node_geodata["children"].keys())
                # There can be a lot of children: if there are too many, take a random selection
                if len(child_ids) > MAX_LOWER_LOCATIONS:
                    child_ids = random.choice(child_ids, MAX_LOWER_LOCATIONS)

                for child_id in child_ids:
                    # Same horrible, shameful hack as above, but going downwards
                    if child_id == "91" and hierarchy_level == 2:
                        continue

                    # Make a separate query for each child id (not a nice way to do this, but difficult otherwise)
                    new_down_messages.extend(
                        self.message_query(datastore, who=who, who_type=who_type,
                                           where_type=LOCATION_TYPES[hierarchy_level-1], where=child_id,
                                           when=when, when_type=when_type,
                                           # Use the level change coef for going one level down from whatever we're on
                                           importance_coefficient=LOC_LEVEL_CHANGE_COEFS[hierarchy_level][1],
                                           limit_records=MAX_EXP_LOCATION_RECORDS, random=random)
                    )

            if len(new_up_messages) + len(new_down_messages):
                log.info("Expanded message set by {} by going up and {} by going down the location hierarchy".format(
                    len(new_up_messages), len(new_down_messages)))
                messages.extend(new_up_messages)
                messages.extend(new_down_messages)

        return (messages, )

    def message_query(self, datastore, who=None, who_type=None, where=None, where_type=None, when=None, when_type=None, ignored_cols=None,
                      importance_coefficient=1., limit_records=None, random=None):
        log.debug("Filtering on {}".format(
            ", ".join(field_name
                      for (field_name, val) in [("who", who), ("who_type", who_type), ("where", where), ("where_type", where_type), ("when", when), ("when_type", when_type)]
                      if val is not None)
        ))

        if ignored_cols is None:
            ignored_cols = []

        query = []
        if where:
            query.append("where == {!r}".format(where))
        if where_type:
            query.append("where_type == {!r}".format(where_type))
        if who:
            query.append("who == {!r}".format(who))
        if who_type:
            query.append("who_type == {!r}".format(who_type))
        if when:
            query.append("when == {!r}".format(when))
        if when_type:
            query.append("when_type == {!r}".format(when_type))
        df = datastore.query(query)

        if limit_records is not None and len(df.index) > limit_records:
            # Too many messages: take a random subsample
            df = df.sample(n=limit_records, random_state=random)

        messages = []
        col_names = [
            col_name for col_name in df 
            if not (
                col_name in ["where", "who", "where_type", "who_type", "when", "when_type"]
                or col_name in ignored_cols 
                or "_outlierness" in col_name
            )
        ]
        df.apply(self._gen_messages, axis=1, args=(col_names, messages, importance_coefficient))

        if log.isEnabledFor(logging.DEBUG):
            for m in messages:
                log.debug("Extracted message {}".format(m))

        log.info("Extracted total {} messages".format(len(messages)))

        return messages
