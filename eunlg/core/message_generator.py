import logging
from math import isnan

from core.domain import Fact, Message
from core.pipeline import NLGPipelineComponent

log = logging.getLogger("root")


class NoMessagesForSelectionException(Exception):
    pass


class MessageGenerator(NLGPipelineComponent):
    """
    NLGPipelineComponent for generating messages from a Pandas DataFrame.

    The DataFrame is assumed to contain columns 'where', 'where_type', 'when' and 'when_type'.
    For all rows and for all columns not in the above list, a message is generated so
    that the above columns define the corresponding features of the message, and one other
    column defines the 'what' and 'what_type'. 'what' is determined by the value of that
    column that row, and the 'what_type' is defined by the title of that column.
    """

    def run(
        self,
        registry,
        random,
        language,
        datastore,
        where_query,
        where_type_query,
        data_query,
        when1_query=None,
        when2_query=None,
        when_type_query="year",
        ignored_cols=None,
    ):
        log.info(
            "Generating messages with where={}, where_type={}, when1={}, when2={}, when_type={}, data={}".format(
                where_query, where_type_query, when1_query, when2_query, when_type_query, data_query,
            )
        )

        if ignored_cols is None:
            ignored_cols = []

        query = []
        if where_query:
            query.append("where=={!r}".format(where_query))

        if where_type_query:
            query.append("where_type=={!r}".format(where_type_query))

        if "when" in datastore.all():
            # The DataFrame only has a 'when' column, not 'when1' and 'when2'
            if when1_query:
                query.append("when=={!r}".format(when1_query))

            if when2_query:
                query.append("when=={!r}".format(when2_query))
        else:
            if when1_query:
                query.append("when1=={!r}".format(when1_query))

            if when2_query:
                query.append("when2=={!r}".format(when2_query))

        if when_type_query:
            query.append("when_type=={!r}".format(when_type_query))

        query = " and ".join(query)
        log.debug('Query: "{}"'.format(query))
        df = datastore.query(query)

        data = data_query
        messages = []
        if data:
            col_names = [name for name in df if data in name]
        else:
            col_names = df
        log.info(ignored_cols)
        col_names = [
            col_name
            for col_name in col_names
            if not (
                col_name in ["where", "when", "when1", "when2", "where_type", "when_type"]
                or col_name in ignored_cols
                or "_outlierness" in col_name
            )
        ]
        df.apply(self._gen_messages, axis=1, args=(col_names, messages))

        if log.getEffectiveLevel() <= 5:
            for m in messages:
                log.debug("Extracted {}".format(m.fact))

        log.info("Extracted total {} messages".format(len(messages)))
        return (messages,)

    def _gen_messages(self, row, col_names, messages, importance_coefficient=1.0, polarity=0.0):
        where = row["where"]
        where_type = row["where_type"]
        when_type = row["when_type"]

        for col_name in col_names:
            what_type = col_name
            what = row[col_name]
            # When value need to be reset for each loop because they may be changed within the loop
            if "when1" in row:
                when_1 = row["when1"] if (row["when1"] and not isnan(row["when1"])) else None
                when_2 = row["when2"]
            else:
                when_1 = when_2 = row["when"]

            outlierness_col_name = col_name + "_outlierness"
            outlierness = row.get(outlierness_col_name, None)
            # For the crime totals, there are two (or three) outliernesses to choose from:
            # _grouped_by_time_place_outlierness,
            # _grouped_by_crime_time_outlierness, and for the monthly statistics
            # _grouped_by_crime_place_year_outlierness
            # Adjusted the code to choose the _time_place_outlierness for now
            if not outlierness:
                outlierness = row.get(col_name + "_grouped_by_time_outlierness", None)

            if what is None or what == "" or (isinstance(what, float) and isnan(what)):
                # 'what' is effectively undefined, do not REALLY generate the message.
                continue

            if callable(importance_coefficient):
                # Allow the importance coefficient to be a function that computes the weight from the field vals
                raise NotImplementedError("Not implemented")

            fact = Fact(
                where=where,
                where_type=where_type,
                when_1=when_1,
                when_2=when_2,
                when_type=when_type,
                what=what,
                what_type=what_type,
                outlierness=outlierness,
            )
            message = Message(facts=fact, importance_coefficient=importance_coefficient, polarity=polarity)
            messages.append(message)
