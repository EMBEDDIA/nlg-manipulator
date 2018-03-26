import logging
from math import isnan

from .pipeline import NLGPipelineComponent
from .message import Fact, Message

log = logging.getLogger('root')


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

    def run(self, registry, random, language, datastore, where_query, where_type_query, when1_query=None, when2_query=None, when_type_query="year", ignored_cols=None):
        log.info("Generating messages with where={}, where_type={}, when1={}, when2={}, when_type={}".format(
            where_query, where_type_query, when1_query, when2_query, when_type_query))

        if ignored_cols is None:
            ignored_cols = []

        query = []
        if where_query:
            query.append("where=={!r}".format(where_query))

        if where_type_query:
            query.append("where_type=={!r}".format(where_type_query))
        
        if when1_query:
            query.append("when1=={!r}".format(when_query))

        if when2_query:
            query.append("when2=={!r}".format(when_query))

        if when_type_query:
            query.append("when_type=={!r}".format(when_type_query))

        query = " and ".join(query)
        log.debug('Query: "{}"'.format(query))
        df = datastore.query(query)
        
        messages = []
        col_names = [
            col_name for col_name in df 
            if not (
                col_name in ["where", "when1", "when2", "where_type", "when_type"]
                or col_name in ignored_cols 
                or "_outlierness" in col_name
            )
        ]
        df.apply(self._gen_messages, axis=1, args=(col_names, messages))

        if log.isEnabledFor(logging.DEBUG):
            for m in messages:
                log.debug("Extracted {}".format(m.fact))

        log.info("Extracted total {} messages".format(len(messages)))
        return (messages, )

    def _gen_messages(self, row, col_names, messages, importance_coefficient=1.0, polarity=0.0):
        where_1 = where_2 = row['where']
        where_type_1 = where_type_2 = row['where_type']
        when_type_1 = when_type_2 = row['when_type']

        for col_name in col_names:            
            what_type_1 = what_type_2 = col_name
            what_1 = what_2 = row[col_name]
            # When value need to be reset for each loop because they may be changed within the loop
            when_1 = row['when1'] if 'when1' in row else None
            when_2 = row['when2']

            outlierness_col_name = col_name + "_outlierness"
            outlierness = row.get(outlierness_col_name, None)

            if what_2 is None or what_2 == "" or (isinstance(what_2, float) and isnan(what_2)):
                # 'what' is effectively undefined, do not REALLY generate the message.
                continue

            if callable(importance_coefficient):
                # Allow the importance coefficient to be a function that computes the weight from the field vals
                importance_coefficient = importance_coefficient(where_2, where_type_2, when_2, when_type_2, what_2, what_type_2)

            fact = Fact(where_1=where_1, where_type_1=where_type_1, where_2=where_2, where_type_2=where_type_2,
                        when_1=when_1, when_type_1=when_type_1, when_2=when_2, when_type_2=when_type_2,
                        what_1=what_1, what_type_1=what_type_1, what_2=what_2, what_type_2=what_type_2,
                        outlierness=outlierness)
            message = Message(facts=fact, importance_coefficient=importance_coefficient, polarity=polarity)
            messages.append(message)
