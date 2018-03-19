import pandas as pd
import numpy as np
from math import sqrt

class ImporterC:

    def __init__(self, fake=False):

        if fake:
            prefix = "fake_"
        else:
            prefix = ""

        self._load_data(prefix)

        ''' Crime data
        self.cd = self._add_ranks_to_crime_data(self.cd, self.cd_interesting_columns)
        self.cd = self._add_outlierness_to_crime_data(self.cd, self.cd_interesting_columns, self.cd_id_columns)
        self.cd = self._sort_columns(self.cd, self.cd_id_columns)
        self.cd.to_csv(prefix + "pyn_crime_ranks_outliers.csv", index=False)
        #'''

        #''' Comparison data
        self.cdc = self._add_ranks_to_comparison_data(self.cdc, self.cdc_interesting_columns)
        self.cdc = self._add_outlierness_to_comparison_data(self.cdc, self.cdc_interesting_columns, self.cdc_id_columns)
        self.cdc = self._sort_columns(self.cdc, self.cdc_id_columns)
        self.cdc.to_csv(prefix + "pyn_crime_y12_comparison_ranks_outliers.csv", index=False)
        #'''

    def _load_data(self, prefix):
        self.crime_data = pd.read_csv(prefix + "pyn_crime.csv")
        self.comparison_data = pd.read_csv(prefix + "pyn_crime_y12_comparison.csv")
        self.crime_data = self._add_year_stamp(self.crime_data, 'when')

        self.cd = self.crime_data
        self.cdc = self.comparison_data

        self.cd_id_columns = ['when', 'when_type', 'where', 'where_type', 'population', 'year']
        self.cdc_id_columns = ['when1', 'when2', 'when_type', 'where', 'where_type']

        self.cd_uninteresting_columns = []
        cd_all_columns = list(self.cd.columns.values)
        self.cd_interesting_columns = [x for x in cd_all_columns if
                                       x not in self.cd_id_columns and x not in self.cd_uninteresting_columns]

        self.cdc_uninteresting_columns = []
        cdc_all_columns = list(self.cdc.columns.values)
        self.cdc_interesting_columns = [x for x in cdc_all_columns if
                                        x not in self.cdc_id_columns and x not in self.cdc_uninteresting_columns]

    def _sort_columns(self, df, id_columns):
        column_names = list(df.columns.values)
        last_columns = [name for name in column_names if name not in id_columns]
        last_columns.sort()
        return df[id_columns + last_columns]

    def _add_ranks_to_crime_data(self, df, ranked_columns):

        grouped_crime_time = df.groupby(["when", "when_type"])
        grouped_crime_place = df.groupby(["where", "where_type", "year", "when_type"])

        for col_name in ranked_columns:
            #print("Crime data rank column: " + col_name)
            # Different rankings:
            #   fixed crime and time (where specific crime was committed most, second most, ... during a specific times)
            ranked_col_name = "{}_grouped_by_crime_time_rank".format(col_name)
            reverse_ranked_col_name = "{}_reverse".format(ranked_col_name)
            #grouped = df.groupby(["when", "when_type"])[col_name]
            grouped = grouped_crime_time[col_name]
            df[ranked_col_name] = grouped.rank(ascending=False, method="dense")
            df[reverse_ranked_col_name] = grouped.rank(ascending=True, method="dense")

            #   fixed crime and place (when specific crime was committed most, second most, ... in specific place,
            #   during some interval)
            ranked_col_name = "{}_grouped_by_crime_place_year_rank".format(col_name)
            reverse_ranked_col_name = "{}_reverse".format(ranked_col_name)
            #grouped = df.groupby(["where", "where_type", "year", "when_type"])[col_name]
            grouped = grouped_crime_place[col_name]
            df[ranked_col_name] = grouped.rank(ascending=False, method="dense")
            df[reverse_ranked_col_name] = grouped.rank(ascending=True, method="dense")

        # Last ranking:
        #   fixed place and time (which crime was committed most, second most, ... in specific place at specific time)
        raw_numbers_columns = [x for x in ranked_columns if 'normalized' not in x]
        normalized_columns = [x for x in ranked_columns if 'normalized' in x]

        raw_ranked_desc = df[raw_numbers_columns].rank(ascending=False, method="dense", axis=1)
        norm_ranked_desc = df[normalized_columns].rank(ascending=False, method="dense", axis=1)

        raw_ranked_asc = df[raw_numbers_columns].rank(ascending=True, method="dense", axis=1)
        norm_ranked_asc = df[normalized_columns].rank(ascending=True, method="dense", axis=1)

        raw_ranked_desc.reset_index(drop=True, inplace=True)
        norm_ranked_desc.reset_index(drop=True, inplace=True)

        raw_ranked_asc.reset_index(drop=True, inplace=True)
        norm_ranked_asc.reset_index(drop=True, inplace=True)

        raw_ranked_desc = raw_ranked_desc.add_suffix("_grouped_by_time_place_rank")
        norm_ranked_desc = norm_ranked_desc.add_suffix("_grouped_by_time_place_rank")

        raw_ranked_asc = raw_ranked_asc.add_suffix("_grouped_by_time_place_rank_reverse")
        norm_ranked_asc = norm_ranked_asc.add_suffix("_grouped_by_time_place_rank_reverse")

        df = pd.concat([df, raw_ranked_asc], axis=1)
        df = pd.concat([df, norm_ranked_asc], axis=1)
        df = pd.concat([df, raw_ranked_desc], axis=1)
        df = pd.concat([df, norm_ranked_desc], axis=1)

        return df

    def _add_outlierness_to_crime_data(self, df, outlierness_columns, id_columns):
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

        rank_columns = [col for col in df.columns.values if "_rank" in col]
        numeric_columns = outlierness_columns

        for column_name in numeric_columns:
            #print("Crime data outliers column: " + column_name)
            #log.debug("Generating outlyingness values for column {}".format(column_name))
            outlierness_ct_column_name = "{}_grouped_by_crime_time_outlierness".format(column_name)
            df[outlierness_ct_column_name] = df.groupby(["when", "when_type"])[column_name].apply(group_outlierness)

            outlierness_ct_column_name = "{}_grouped_by_crime_place_year_outlierness".format(column_name)
            df[outlierness_ct_column_name] = df.groupby(["where", "where_type", "year", "when_type"])[column_name].apply(group_outlierness)

        # Last outlierness:
        #   fixed place and time (which crime was committed most, second most, ... in specific place at specific time)
        raw_numbers_columns = [x for x in numeric_columns if 'normalized' not in x]
        normalized_columns = [x for x in numeric_columns if 'normalized' in x]

        raw_outlierness = df[raw_numbers_columns]
        norm_outlierness = df[normalized_columns]

        raw_outlierness.reset_index(drop=True, inplace=True)
        norm_outlierness.reset_index(drop=True, inplace=True)

        for i in range(len(raw_outlierness)):
            raw_outlierness.iloc[i] = group_outlierness(raw_outlierness.iloc[i])
            norm_outlierness.iloc[i] = group_outlierness(norm_outlierness.iloc[i])

        raw_outlierness = raw_outlierness.add_suffix("_grouped_by_time_place_outlierness")
        norm_outlierness = norm_outlierness.add_suffix("_grouped_by_time_place_outlierness")

        df = pd.concat([df, raw_outlierness], axis=1)
        df = pd.concat([df, norm_outlierness], axis=1)

        for rank_column_name in rank_columns:
            normal_column_name = rank_column_name.replace("_reverse", "").replace("_rank", "")
            outlierness_rank_column_name = "{}_outlierness".format(rank_column_name)
            outlierness_normal_column_name = "{}_outlierness".format(normal_column_name)
            df[outlierness_rank_column_name] = df[outlierness_normal_column_name]

        non_numeric_columns = id_columns
        for column_name in non_numeric_columns:
            #log.debug("Generating outlyingness values for column {}".format(column_name))
            outlierness_column_name = "{}_outlierness".format(column_name)
            df[outlierness_column_name] = 0.5

        return df

    def _add_year_stamp(self, df, time_column):
        df["year"] = list(df[time_column].apply(lambda x: x[:4]))
        return df

    # semi copy paste garbage
    def _add_ranks_to_comparison_data(self, df, ranked_columns):

        for col_name in ranked_columns:
            # Different rankings:
            #   fixed crime and time (where specific crime was committed most, second most, ... during a specific times)
            ranked_col_name = "{}_grouped_by_crime_time_rank".format(col_name)
            reverse_ranked_col_name = "{}_reverse".format(ranked_col_name)
            grouped = df.groupby(["when1", "when2", "when_type"])[col_name]
            df[ranked_col_name] = grouped.rank(ascending=False, method="dense")
            df[reverse_ranked_col_name] = grouped.rank(ascending=True, method="dense")

        # Last ranking:
        #   fixed place and time (which crime was committed most, second most, ... in specific place at specific time)
        raw_change_columns = [x for x in ranked_columns if 'normalized' not in x and 'percentage' not in x]
        normalized_change_columns = [x for x in ranked_columns if 'normalized' in x and 'percentage' not in x]
        percentage_change_columns = [x for x in ranked_columns if 'normalized' not in x and 'percentage' in x]
        normalized_percentage_change_columns = [x for x in ranked_columns if 'normalized' in x and 'percentage' in x]

        raw_change_ranked_desc = df[raw_change_columns].rank(ascending=False, method="dense", axis=1)
        normalized_change_desc = df[normalized_change_columns].rank(ascending=False, method="dense", axis=1)
        percentage_change_ranked_desc = df[percentage_change_columns].rank(ascending=False, method="dense", axis=1)
        normalized_percentage_change_desc = df[normalized_percentage_change_columns].rank(ascending=False,
                                                                                          method="dense", axis=1)

        raw_change_ranked_asc = df[raw_change_columns].rank(ascending=True, method="dense", axis=1)
        normalized_change_asc = df[normalized_change_columns].rank(ascending=True, method="dense", axis=1)
        percentage_change_ranked_asc = df[percentage_change_columns].rank(ascending=True, method="dense", axis=1)
        normalized_percentage_change_asc = df[normalized_percentage_change_columns].rank(ascending=True,
                                                                                          method="dense", axis=1)

        raw_change_ranked_desc = raw_change_ranked_desc.add_suffix("_grouped_by_time_place_rank")
        normalized_change_desc = normalized_change_desc.add_suffix("_grouped_by_time_place_rank")
        percentage_change_ranked_desc = percentage_change_ranked_desc.add_suffix("_grouped_by_time_place_rank")
        normalized_percentage_change_desc = normalized_percentage_change_desc.add_suffix("_grouped_by_time_place_rank")

        raw_change_ranked_asc = raw_change_ranked_asc.add_suffix("_grouped_by_time_place_rank_reverse")
        normalized_change_asc = normalized_change_asc.add_suffix("_grouped_by_time_place_rank_reverse")
        percentage_change_ranked_asc = percentage_change_ranked_asc.add_suffix("_grouped_by_time_place_rank_reverse")
        normalized_percentage_change_asc = normalized_percentage_change_asc.add_suffix("_grouped_by_time_place_rank_reverse")

        df = pd.concat([df, raw_change_ranked_desc], axis=1)
        df = pd.concat([df, normalized_change_desc], axis=1)
        df = pd.concat([df, percentage_change_ranked_desc], axis=1)
        df = pd.concat([df, normalized_percentage_change_desc], axis=1)
        df = pd.concat([df, raw_change_ranked_asc], axis=1)
        df = pd.concat([df, normalized_change_asc], axis=1)
        df = pd.concat([df, percentage_change_ranked_asc], axis=1)
        df = pd.concat([df, normalized_percentage_change_asc], axis=1)

        return df

    def _add_outlierness_to_comparison_data(self, df, outlierness_columns, id_columns):
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

        rank_columns = [col for col in df.columns.values if "_rank" in col]
        numeric_columns = outlierness_columns

        for column_name in numeric_columns:
            # log.debug("Generating outlyingness values for column {}".format(column_name))
            outlierness_ct_column_name = "{}_grouped_by_crime_time_outlierness".format(column_name)
            df[outlierness_ct_column_name] = df.groupby(["when1", "when2", "when_type"])[column_name].apply(group_outlierness)

        # Last outlierness:
        #   fixed place and time (which crime was committed most, second most, ... in specific place at specific time)
        raw_change_columns = [x for x in numeric_columns if 'normalized' not in x and 'percentage' not in x]
        normalized_change_columns = [x for x in numeric_columns if 'normalized' in x and 'percentage' not in x]
        percentage_change_columns = [x for x in numeric_columns if 'normalized' not in x and 'percentage' in x]
        normalized_percentage_change_columns = [x for x in numeric_columns if 'normalized' in x and 'percentage' in x]

        raw_change_outlierness = df[raw_change_columns]
        normalized_change_outlierness = df[normalized_change_columns]
        percentage_change_outlierness = df[percentage_change_columns]
        normalized_percentage_change_outlierness = df[normalized_percentage_change_columns]

        #reset index???

        for i in range(len(raw_change_outlierness)):
            raw_change_outlierness.iloc[i] = group_outlierness(raw_change_outlierness.iloc[i])
            normalized_change_outlierness.iloc[i] = group_outlierness(normalized_change_outlierness.iloc[i])
            percentage_change_outlierness.iloc[i] = group_outlierness(percentage_change_outlierness.iloc[i])
            normalized_percentage_change_outlierness.iloc[i] = group_outlierness(normalized_percentage_change_outlierness.iloc[i])

        raw_change_outlierness = raw_change_outlierness.add_suffix("_grouped_by_time_place_outlierness")
        normalized_change_outlierness = normalized_change_outlierness.add_suffix("_grouped_by_time_place_outlierness")
        percentage_change_outlierness = percentage_change_outlierness.add_suffix("_grouped_by_time_place_outlierness")
        normalized_percentage_change_outlierness = normalized_percentage_change_outlierness.add_suffix("_grouped_by_time_place_outlierness")

        df = pd.concat([df, raw_change_outlierness], axis=1)
        df = pd.concat([df, normalized_change_outlierness], axis=1)
        df = pd.concat([df, percentage_change_outlierness], axis=1)
        df = pd.concat([df, normalized_percentage_change_outlierness], axis=1)

        for rank_column_name in rank_columns:
            normal_column_name = rank_column_name.replace("_reverse", "").replace("_rank", "")
            outlierness_rank_column_name = "{}_outlierness".format(rank_column_name)
            outlierness_normal_column_name = "{}_outlierness".format(normal_column_name)
            df[outlierness_rank_column_name] = df[outlierness_normal_column_name]

        non_numeric_columns = id_columns
        for column_name in non_numeric_columns:
            # log.debug("Generating outlyingness values for column {}".format(column_name))
            outlierness_column_name = "{}_outlierness".format(column_name)
            df[outlierness_column_name] = 0.5

        return df
