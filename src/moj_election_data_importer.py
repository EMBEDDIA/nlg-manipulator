from datetime import datetime
import pandas as pd
import numpy as np
from math import isnan, sqrt

from core import NLGPipelineComponent

import logging
log = logging.getLogger('root')


class Importer(NLGPipelineComponent):

    """
        Key for determining locations of values in the MOJ data. Lines are of the form:
        "<field name>": (<field-length>, <field-start-new-format>, <field-start-old-format>, <field-type>)"

        field-length, field-start-new-format and field-start-old-format are expressed in
        characters in the underlying CSV represenations.

        A field is extracted from character range line[field-start:field-start+field-length],
        where field-start is either field-start-old-format or field-start-new-format depending
        on parametrization. Note that the separator characters are not within this range.

        field-type encodes how the field value should be interpreted. Possible values are:
            s   String. The underlying value is stripped of spaces at start and end.
            i   Integer
            p   Percetage, decimal value with a single decimal place. MOJ does __not__ use
                decimal separators, so the value 10.1 is written as "101" in the underlying
                CSV representation.
            d   Decimal, decimal value with three decimal places. As with percentages, MOJ
                does __not__ use decimal separators, so the value 1.001 is written as
                "1001" in the underlying CSV representation.
            b   Boolean.

        Note that all fields are padded, so that the integer "1" in a 5-digit field is
        written as "00001". Spaces are used as padding with string values.

        field-start-old-format refers to the 2012 municipal election data format, whereas the
        new format refers to the format used in the (upcoming) 2017 elections.
    """
    _regional_key = {
        "election_type": (4, 1, 1, "s"),
        #
        "electoral_district_id": (2, 6, 6, "i"),
        "municipality_id": (3, 9, 9, "i"),
        "polling_district_id": (4, 15, 15, "s"),
        #
        "area_type": (1, 13, 13, "s"),
        "area_name_fi": (40, 35, 28, "s"),
        "area_name_sv": (40, 76, 69, "s"),
        #
        "municipality_type": (1, 117, 110, "i"),
        "municipality_language_distribution": (1, 119, 112, "i"),
        #
        "eligible_voters": (7, 121, 114, "i"),
        "eligible_voters_male": (7, 129, 122, "i"),
        "eligible_voters_female": (7, 137, 130, "i"),
        #
        "number_of_seats": (5, 169, 162, "i"),
        #
        "advanced_voting_turnout_percentage": (4, 430, 327, "p"),
        "election_day_turnout_percentage": (4, 435, 332, "p"),
        "total_voter_turnout_percentage": (4, 440, 337, "p"),
        #
        "count_progress_percentage": (4, 533, 415, "p"),
        "count_phase": (1, 538, 420, "s"),
        "last_updated": (14, 540, 422, "t"),
    }

    _nominator_key = {
        "election_type": (4, 1, 1, "s"),
        #
        "electoral_district_id": (2, 6, 6, "i"),
        "municipality_id": (3, 9, 9, "i"),
        "polling_district_id": (4, 15, 15, "s"),
        #
        "area_type": (1, 13, 13, "s"),
        "area_name_fi": (40, 62, 48, "s"),
        "area_name_sv": (40, 103, 89, "s"),
        #
        "permanent_party_id": (6, 28, None, "s"),
        "party_order_number": (2, 35, 28, "i"),
        "party_name_short_fi": (6, 41, 34, "s"),
        "party_name_short_sv": (6, 48, 41, "s"),
        "party_name_short_en": (6, 55, None, "s"),
        "party_name_fi": (100, 144, 130, "s"),
        "party_name_sv": (100, 245, 231, "s"),
        "party_name_en": (100, 346, None, "s"),
        #
        "min_candidate_number": (4, 447, 332, "i"),
        "max_candidate_number": (4, 452, 337, "i"),
        #
        "electoral_alliance_id": (2, 457, 342, "i"),
        "electoral_alliance_name_fi": (40, 460, 345, "s"),
        "electoral_alliance_name_sv": (40, 501, 386, "s"),
        #
        "total_votes_previous_election": (7, 569, 454, "i"),
        "percentage_votes_previous_election": (4, 577, 472, "p"),
        "seats_previous_election": (5, 592, 477, "i"),
        #
        "total_votes": (7, 664, 549, "i"),
        "percentage_votes": (4, 682, 567, "p"),
        "seats": (5, 687, 572, "i"),
        #
        "total_votes_change": (8, 693, 578, "i"),
        "percentage_votes_change": (5, 702, 587, "p"),
        "seats_change": (6, 708, 593, "i"),
        #
        "count_phase": (1, 732, 617, "s"),
        "last_updated": (14, 734, 619, "t"),
    }

    _candidate_key = {
        "election_type": (4, 1, 1, "s"),
        #
        "electoral_district_id": (2, 6, 6, "i"),
        "municipality_id": (3, 9, 9, "i"),
        "polling_district_id": (4, 15, 15, "s"),
        #
        "area_type": (1, 13, 13, "s"),
        "area_name_fi": (40, 70, 56, "s"),
        "area_name_sv": (40, 111, 97, "s"),
        #
        "permanent_party_id": (6, 28, None, "s"),
        "party_order_number": (2, 35, 28, "i"),
        "party_name_short_fi": (6, 44, 37, "s"),
        "party_name_short_sv": (6, 51, 44, "s"),
        "party_name_short_en": (6, 58, None, "s"),
        #
        "candidate_id": (4, 65, 51, "i"),
        "first_name": (50, 152, 138, "s"),
        "last_name": (50, 203, 189, "s"),
        "gender": (1, 254, 240, "i"),
        "age_on_election_day": (3, 256, 242, "i"),
        "profession": ((200, 100), 260, 246, "s"),
        "first_language": (2, 547, None, "s"),
        "is_mep": (1, 550, 433, "i"),
        "is_mp": (1, 552, 435, "i"),
        "is_councillor": (1, 554, 437, "i"),
        #
        "total_votes_previous_election": (7, 569, 452, "i"),
        "total_votes": (7, 593, 476, "i"),
        "percentage_votes": (4, 611, 494, "p"),
        #
        "election_result": (1, 616, 499, "i"),
        "comparison_number": (10, 618, 501, "d"),
        "place": (4, 629, None, "i"),
        "final_place": (4, 634, None, "i"),
        #
        "count_phase": (1, 641, 514, "s"),
        "last_updated": (1, 643, 516, "t")
    }

    def __init__(self, spec=2017):
        if spec not in [2012, 2017]:
            raise ValueError("Spec must be 2012 or 2017")
        self._spec = spec

    @property
    def spec(self):
        return self._spec

    def load_meta(self, filepath):
        log.debug("Loading MoJ election metadata from {}".format(filepath))
        data = self._load_data(filepath, Importer._regional_key)
        data = self.normalize_where(data)
        return data

    def load_party_results(self, filepath):
        log.debug("Loading MoJ election party data from {}".format(filepath))
        party_data = self._load_data(filepath, Importer._nominator_key)

        log.debug("Normalizing party data")
        party_data = self._normalize_party_data(party_data)

        log.debug("Converting to new time system")
        party_data = self._add_when_columns(party_data)

        log.debug("Converting booleans")
        party_data = self._convert_booleans(party_data)

        log.debug("Adding ranks to party data")
        party_data = self._add_ranks(party_data)

        log.debug("Adding outlierness values")
        party_data = self._add_outlierness(party_data)

        return party_data

    def load_candidate_results(self, filepath):
        log.debug("Loading MoJ election candidate data from {}".format(filepath))
        candidate_data = self._load_data(filepath, Importer._candidate_key)

        log.debug("Normalizing candidate data")
        candidate_data = self._normalize_candidate_data(candidate_data)

        log.debug("Converting to new time system")
        candidate_data = self._add_when_columns(candidate_data)

        log.debug("Converting booleans")
        candidate_data = self._convert_booleans(candidate_data)

        log.debug("Adding ranks to candidate data")
        candidate_data = self._add_ranks(candidate_data)

        log.debug("Adding outlierness values")
        candidate_data = self._add_outlierness(candidate_data)

        return candidate_data

    def _load_data(self, path, metadata_dict):
        data = []
        with open(path, encoding='iso-8859-1') as f:
            for line in f:
                items = {}
                for key in metadata_dict:
                    metadata = metadata_dict[key]
                    field_type = metadata[3]
                    field_length = metadata[0]
                    if isinstance(field_length, tuple):
                        if self.spec == 2012:
                            field_length = field_length[1]
                        else:
                            field_length = field_length[0]
                    if self.spec == 2012:
                        if not metadata[2]:
                            items[key] = float('NaN')
                            continue
                        field_start = metadata[2] - 1
                    else:
                        field_start = metadata[1] - 1
                    field_end = field_start + field_length

                    try:
                        field_value = self._get_value(line, field_start, field_end, field_type)
                        items[key] = field_value
                    except ValueError as ex:
                        items[key] = None

                data.append(items)

        df = pd.DataFrame(data)
        return df

    def _get_value(self, line, field_start, field_end, field_type):
        value = line[field_start:field_end]
        original_value = value

        if field_type not in ["s", "t", "i", "p", "d"]:
            raise ValueError("Invalid field type:", field_type)

        if field_type == "s":
            return value.strip()
        elif field_type == "t":
            return datetime.strptime(value,"%Y%m%d%H%M%S")

        value = value.strip()
        if value:
            value = int(value)
        else:
            return 0

        if field_type == "i":
            return value
        elif field_type == "p":
            return value / 10
        elif field_type == "d":
            return value / 1000

        raise ValueError("Value '{}' did not match any matcher but was of valid type {}".format(original_value, field_type))

    def _add_ranks(self, df):
        ranked_columns = list(df.select_dtypes(include=[np.number], exclude=["bool"]).columns.values)
        ranked_columns = [col for col in ranked_columns if col not in["gender", "election_result", "when", "percentage_votes_change"]]
        for col_name in ranked_columns:
            log.debug("Generating ranked columns from {}".format(col_name))
            ranked_col_name = "{}_rank".format(col_name)
            reverse_ranked_col_name = "{}_reverse".format(ranked_col_name)
            grouped = df.groupby(["where", "where_type", "when", "when_type"])[col_name]
            df[ranked_col_name] = grouped.rank(ascending=False, method="min")
            df[reverse_ranked_col_name] = grouped.rank(ascending=True, method="min")
            # Get rid of the nonsensical "X lost 2 votes and gained 7th most votes" sentences here by setting
            # _change_rank to n/a if the corresponding _change is negative and _change_rank_reverse to n/a if
            # the _change is positive
            if "change" in col_name:
                df.loc[df[col_name] <= 0, ranked_col_name] = float('nan')
                df.loc[df[col_name] >= 0, reverse_ranked_col_name] = float('nan')
        return df

    def _add_outlierness(self, df):
        const_max_out = 2

        def outlierness(val, count, min_val, q1, q2, q3, max_val):
            size_weight = sqrt(1 / sqrt(count))
            if q1 == q3:
                if val == q2:
                    return 0.5 * size_weight
                if val > q3:
                    return 0.5 + (const_max_out - 0.5) * (val - q2) / (max_val - q2) * size_weight
                if val < q1:
                    return 0.5 + (const_max_out - 0.5) * (q2 - val) / (q2 - min_val) * size_weight
            else:
                if (q1 < val) and (val < q3):
                    return min(
                        outlierness(q1, count, min_val, q1, q2, q3, max_val),
                        outlierness(q3, count, min_val, q1, q2, q3, max_val)
                    ) * size_weight
                return abs(val - q2) / (q3 - q1) * size_weight
            
        def group_outlierness(grp):
            quantiles = grp.quantile([.25, .5, .75])
            min_val = grp.min()
            max_val = grp.max()
            q1 = quantiles[0.25]
            q2 = quantiles[0.5]
            q3 = quantiles[0.75]
            return grp.apply(outlierness, args=(grp.size, min_val, q1, q2, q3, max_val))

        numeric_columns = list(df.select_dtypes(include=[np.number]).columns.values)
        rank_columns = [col for col in numeric_columns if "_rank" in col]
        numeric_columns = [col for col in numeric_columns if not ("_rank" in col or col in ["election_result", "gender", "when"])]

        for column_name in numeric_columns:
            log.debug("Generating outlyingness values for column {}".format(column_name))
            outlierness_column_name = "{}_outlierness".format(column_name)
            df[outlierness_column_name] = df.groupby(["where", "where_type", "when", "when_type"])[column_name].apply(group_outlierness)

        for rank_column_name in rank_columns:
            normal_column_name = rank_column_name.replace("_reverse", "").replace("_rank", "")
            outlierness_rank_column_name = "{}_outlierness".format(rank_column_name)
            outlierness_normal_column_name = "{}_outlierness".format(normal_column_name)
            df[outlierness_rank_column_name] = df[outlierness_normal_column_name]

        non_numeric_columns = [col for col in list(df.select_dtypes(exclude=[np.number]).columns.values) if col not in ["where", "who", "when", "where_type", "who_type", "when_type"]]
        non_numeric_columns.extend([col for col in ["gender", "election_result"] if col in df.columns.values])

        for column_name in non_numeric_columns:
            log.debug("Generating outlyingness values for column {}".format(column_name))
            outlierness_column_name = "{}_outlierness".format(column_name)
            # Do not change this
            df[outlierness_column_name] = 0.5
            
        return df  

    def _add_when_columns(self, df):
        previous_columns = [col for col in df.columns.values if "_previous_election" in col]
        df["when"] = 2017
        df["when_type"] = "year"
        string_columns = list(df.select_dtypes(exclude=[np.number]).columns.values)
        string_columns.extend(col for col in ["gender"] if col in df.columns.values)
        df_2012 = df.loc[:, string_columns]
        df_2012.loc[:, "when"] = 2012
        for col in previous_columns:
            df_2012.loc[:, col[:-18]] = df.loc[:, col]
        df_new = df.append(df_2012).reset_index(drop=True)
        df_new = df_new.drop(previous_columns, axis=1)
        return df_new

    def _convert_booleans(self, df):
        numeric_columns = list(df.select_dtypes(include=[np.number]).columns.values)
        for col_name in numeric_columns:
            if col_name.startswith("is_"):
                log.debug("Converting column {} to boolean".format(col_name))
                df[col_name] = df[col_name].astype('bool')
        return df

    def _normalize_party_data(self, data):
        data["who"] = data["party_name_short_fi"]
        data["who_type"] = "party"
        data = self.normalize_where(data)
        precinct_rows = data["where_type"] == "P"
        # Set nonexistent data to nan instead of 0
        data.loc[precinct_rows, ["seats", "seats_change", "seats_previous_election", "total_votes_change", "total_votes_previous_election", "percentage_votes_change", "percentage_votes_previous_election"]] = float("NaN")
        return data[[
            "where",
            "where_type",
            "who",
            "who_type",
            "party_name_short_fi",
            "party_name_short_sv",
            "party_name_fi",
            "party_name_sv",
            "seats",
            "seats_change",
            "seats_previous_election",
            "total_votes",
            "total_votes_change",
            "total_votes_previous_election",
            "percentage_votes",
            "percentage_votes_change",
            "percentage_votes_previous_election",
        ]]

    def _normalize_candidate_data(self, data):
        def to_unique_id(record):
            return "{}-{}".format(record["municipality_id"], record["candidate_id"])
        def to_name(record):
            return "{} {}".format(record["first_name"], record["last_name"])
        data['who'] = data.apply(to_unique_id, axis=1)
        data['name'] = data.apply(to_name, axis=1)
        data.rename(columns={'party_name_short_fi': 'party'}, inplace=True)
        data["who_type"] = "candidate"
        data = self.normalize_where(data)
        precinct_rows = data["where_type"] == "P"
        # Set nonexistent data to nan instead of 0
        data.loc[precinct_rows, ["total_votes_previous_election"]] = float("NaN")
        return data[[
            "where",
            "where_type",
            "who",
            "who_type",
            "name",
            "gender",
            "total_votes",
            "total_votes_previous_election",
            "percentage_votes",
            "party",
            "is_councillor",
            "is_mep",
            "is_mp",
            "election_result",
        ]]

    def normalize_where(self, df):
        # Closure'd function for determining "where"
        def normalize_where_value(row):
            district = row["electoral_district_id"]
            municipality = row["municipality_id"]
            station = row["polling_district_id"]
            if not district or isnan(district) or district == "**":
                where = "fi"
            elif not municipality or isnan(municipality) or municipality == "***":
                where = str(int(district))
            elif not station or station == "****":
                where = str(int(municipality))
            else:
                where = "M{}: {}".format(int(municipality), station)
            return where

        # Closure'd function for determining "where_type"
        def normalize_where_type(row):
            district = row["electoral_district_id"]
            municipality = row["municipality_id"]
            station = row["polling_district_id"]
            if not district or isnan(district) or district == "**":
                where_type = "C"
            elif not municipality or isnan(municipality) or municipality == "***":
                where_type = "D"
            elif not station or station == "****":
                where_type = "M"
            else:
                where_type = "P"
            return where_type

        # Apply the above functions
        df["where"] = df.apply(normalize_where_value, axis=1)
        df["where_type"] = df.apply(normalize_where_type, axis=1)

        return df
