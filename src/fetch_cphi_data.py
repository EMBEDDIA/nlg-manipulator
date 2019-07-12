import pandas as pd
import numpy as np
from math import sqrt
import math
import os.path
import columns as cls
import paramconfig as prmcnf
from operator import itemgetter
import itertools


def rank_df(df, ranked_columns):
    ranked_columns = ranked_columns

    grouped_cphi_time = df.groupby(["when", "when_type"])
    #grouped_cphi_place = df.groupby(["where", "where_type", "when", "when_type"])

    for col_name in ranked_columns:
        ranked_col_name = "{}_grouped_by_cphi_time_rank".format(col_name)
        reverse_ranked_col_name = "{}_reverse".format(ranked_col_name)
        grouped = grouped_cphi_time[col_name]
        df[ranked_col_name] = grouped.rank(ascending=False, method="dense", na_option='keep')
        df[reverse_ranked_col_name] = grouped.rank(ascending=True, method="dense", na_option='keep')
    return df


def add_outlierness_to_cphi_data(df, outlierness_columns, id_columns):
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
        outlierness_ct_column_name = "{}_grouped_by_cphi_time_outlierness".format(column_name)
        df[outlierness_ct_column_name] = df.groupby(["when", "when_type"])[column_name].apply(group_outlierness)

            # outlierness_ct_column_name = "{}_grouped_by_crime_place_year_outlierness".format(column_name)
            # df[outlierness_ct_column_name] = df.groupby(["where", "where_type", "year", "when_type"])[column_name].apply(group_outlierness)
            # df.loc[df['when_type'] == 'year', outlierness_ct_column_name] = np.nan

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


def flatten(df):
    '''
    Flatten a data frame so that each field contains a single value.
    '''

    new_df = pd.DataFrame()
    names = list(df.columns)

    new_columns = names.pop(0)

    initial_content = []
    values = df.values.tolist()
    values = [value[1:] for value in values]
    values = list(itertools.chain.from_iterable(values))
    values_n_flags = pd.DataFrame(values)[0].str.split(' ', expand=True)
    values_n_flags = values_n_flags.rename(columns={0:'value', 1:'flag'})

    for line in df[new_columns]:
        for when in names:
            initial_content.append((',').join([line, when]))
    new_columns = (',').join([new_columns, 'when'])
    new_df[new_columns] = initial_content

    columns = new_columns.split(',')
    new_df = new_df[new_columns].str.split(',', expand=True)
    new_df = new_df.rename(columns=dict(zip(list(new_df.columns), columns)))
    new_df = new_df.rename(columns={'geo\\time':'where'})

    new_df[['value', 'flag']] = values_n_flags

    new_df = new_df.replace(to_replace=':', value=np.nan)

    new_df = pd.pivot_table(new_df, index =['where', 'when'], columns =['unit', 'indic'], values = 'value', aggfunc='first')
    new_df.reset_index(level=['where', 'when'], inplace=True)
    new_df.columns = new_df.columns.to_flat_index()
    new_df.columns = [(column[0]+column[1]).replace('-', '_').lower() for column in new_df.columns]
    data = [pd.to_numeric(new_df[s], errors='ignore') for s in new_df.columns]
    new_df = pd.concat(data, axis=1, keys=[s.name for s in data])

    return new_df


def run():

    df = pd.read_csv('../database/ei_cphi_m.tsv', sep='\t')

    # Flatten DataFrame
    df = flatten(df)

    # Add when_type and where_type
    where_type = ['C'] * df.shape[0]
    when_type = ['month'] * df.shape[0]

    df['where_type'] = where_type
    df['when_type'] = when_type

    id_columns = ['when', 'when_type', 'where', 'where_type']

    # Rank value columns
    df = rank_df(df, [column for column in df.columns if column not in id_columns])

    # Add outlierness to data
    outlierness_columns = [column for column in df.columns if column not in id_columns]
    df = add_outlierness_to_cphi_data(df, outlierness_columns, id_columns)
    # Remove redundant spaces
    df['when'] = [when.strip(' ') for when in df['when']]
    # Lowercase countrie names to match Valtteri style
    df['where'] = [where.lower() for where in df['where']]

    df.to_csv(os.path.join(os.path.dirname(__file__), '../data/cphi.csv'))


    # print('Converter')
    # ConverterC()

    # print('Importer')
    # ImporterC()

    # print('Trend Finder')
    # TrendFinder()


# class ImporterC:

#     def __init__(self, fake=False):

#         if fake:
#             prefix = "fake_"
#         else:
#             prefix = ""

#         self._load_data(prefix)

#         # Crime data
#         self.cd = self._add_ranks_to_cphi_data(self.cd, self.cd_interesting_columns)
#         self.cd = self._add_outlierness_to_cphi_data(self.cd, self.cd_interesting_columns, self.cd_id_columns)
#         self.cd = self._sort_columns(self.cd, self.cd_id_columns)
#         self.cd.to_csv(os.path.join(os.path.dirname(__file__), '../data/' + prefix + "crime_pyn_ranks_outliers.csv"), index=False)

#         print("Crime data half way")

#         self.bccd = self._add_ranks_to_cphi_data(self.bccd, self.bccd_interesting_columns)
#         self.bccd = self._add_outlierness_to_cphi_data(self.bccd, self.bccd_interesting_columns, self.bccd_id_columns)
#         self.bccd = self._sort_columns(self.bccd, self.bccd_id_columns)
#         self.bccd.to_csv(os.path.join(os.path.dirname(__file__), '../data/' + prefix + "bc_crime_pyn_ranks_outliers.csv"), index=False)

#         print("Crime data ready")

#         # Comparison data
#         self.cdc = self._add_ranks_to_comparison_data(self.cdc, self.cdc_interesting_columns)
#         self.cdc = self._add_outlierness_to_comparison_data(self.cdc, self.cdc_interesting_columns, self.cdc_id_columns)
#         self.cdc = self._sort_columns(self.cdc, self.cdc_id_columns)
#         self.cdc.to_csv(os.path.join(os.path.dirname(__file__), '../data/' + prefix + "crime_pyn_comp_ranks_outliers.csv"), index=False)

#         print("Comp data half way")

#         self.bccdc = self._add_ranks_to_comparison_data(self.bccdc, self.bccdc_interesting_columns)
#         self.bccdc = self._add_outlierness_to_comparison_data(self.bccdc, self.bccdc_interesting_columns, self.bccdc_id_columns)
#         self.bccdc = self._sort_columns(self.bccdc, self.bccdc_id_columns)
#         self.bccdc.to_csv(os.path.join(os.path.dirname(__file__), '../data/' + prefix + "bc_crime_pyn_comp_ranks_outliers.csv"), index=False)

#         print("Comp data ready")

#     def _load_data(self, prefix):

#         self.cd = pd.read_csv(os.path.join(os.path.dirname(__file__), '../data/' + prefix + "crime_pyn.csv"))
#         self.cdc = pd.read_csv(os.path.join(os.path.dirname(__file__), '../data/' + prefix + "crime_pyn_comp.csv"))
#         self.bccd = pd.read_csv(os.path.join(os.path.dirname(__file__), '../data/' + prefix + "bc_crime_pyn.csv"))
#         self.bccdc = pd.read_csv(os.path.join(os.path.dirname(__file__), '../data/' + prefix + "bc_crime_pyn_comp.csv"))

#         self.cd_id_columns = ['when', 'when_type', 'where', 'where_type', 'population', 'year']
#         self.cdc_id_columns = ['when1', 'when2', 'when_type', 'where', 'where_type']
#         self.bccd_id_columns = ['when', 'when_type', 'where', 'where_type', 'population', 'year']
#         self.bccdc_id_columns = ['when1', 'when2', 'when_type', 'where', 'where_type']

#         self.cd_uninteresting_columns = ['all_total', 'all_total_normalized']
#         cd_all_columns = list(self.cd.columns.values)
#         self.cd_interesting_columns = [x for x in cd_all_columns if
#                                        x not in self.cd_id_columns and x not in self.cd_uninteresting_columns]

#         self.cdc_uninteresting_columns = ['all_total_change', 'all_total_normalized_change', 'all_total_percentage_change', 'all_total_normalized_percentage_change']
#         cdc_all_columns = list(self.cdc.columns.values)
#         self.cdc_interesting_columns = [x for x in cdc_all_columns if
#                                         x not in self.cdc_id_columns and x not in self.cdc_uninteresting_columns]

#         self.bccd_uninteresting_columns = ['all_total', 'all_total_normalized']
#         bccd_all_columns = list(self.bccd.columns.values)
#         self.bccd_interesting_columns = [x for x in bccd_all_columns if
#                                        x not in self.bccd_id_columns and x not in self.bccd_uninteresting_columns]

#         self.bccdc_uninteresting_columns = ['all_total_change', 'all_total_normalized_change', 'all_total_percentage_change', 'all_total_normalized_percentage_change']
#         bccdc_all_columns = list(self.bccdc.columns.values)
#         self.bccdc_interesting_columns = [x for x in bccdc_all_columns if
#                                         x not in self.bccdc_id_columns and x not in self.bccdc_uninteresting_columns]

#     def _sort_columns(self, df, id_columns):
#         column_names = list(df.columns.values)
#         last_columns = [name for name in column_names if name not in id_columns]
#         last_columns.sort()
#         return df[id_columns + last_columns]

#     def _add_ranks_to_cphi_data(self, df, ranked_columns):

#         grouped_crime_time = df.groupby(["when", "when_type"])
#         grouped_crime_place = df.groupby(["where", "where_type", "year", "when_type"])

#         for col_name in ranked_columns:
#             #print("Crime data rank column: " + col_name)
#             # Different rankings:
#             #   fixed crime and time (where specific crime was committed most, second most, ... during a specific times)
#             ranked_col_name = "{}_grouped_by_crime_time_rank".format(col_name)
#             reverse_ranked_col_name = "{}_reverse".format(ranked_col_name)
#             grouped = grouped_crime_time[col_name]
#             df[ranked_col_name] = grouped.rank(ascending=False, method="dense")
#             df[reverse_ranked_col_name] = grouped.rank(ascending=True, method="dense")

#             # Saying that a place with zero crimes has the most crimes doesn't really make much sense, so we're dropping
#             # those
#             df.loc[df[col_name] == 0, ranked_col_name] = np.nan

#             #   fixed crime and place (when specific crime was committed most, second most, ... in specific place,
#             #   during some interval)
#             ranked_col_name = "{}_grouped_by_crime_place_year_rank".format(col_name)
#             reverse_ranked_col_name = "{}_reverse".format(ranked_col_name)
#             grouped = grouped_crime_place[col_name]
#             df[ranked_col_name] = grouped.rank(ascending=False, method="dense")
#             df[reverse_ranked_col_name] = grouped.rank(ascending=True, method="dense")

#             # Saying that a place with zero crimes has the most crimes doesn't really make much sense, so we're dropping
#             # those
#             df.loc[df[col_name] == 0, ranked_col_name] = np.nan

#             # Set ranks for monthly comparisons to zero for the rows containing yearly totals
#             df.loc[df['when_type'] == 'year', ranked_col_name] = np.nan
#             df.loc[df['when_type'] == 'year', reverse_ranked_col_name] = np.nan

#         # Last ranking:
#         #   fixed place and time (which crime was committed most, second most, ... in specific place at specific time)
#         raw_numbers_columns = [x for x in ranked_columns if 'normalized' not in x]
#         normalized_columns = [x for x in ranked_columns if 'normalized' in x]

#         raw_ranked_desc = df[raw_numbers_columns].rank(ascending=False, method="dense", axis=1)
#         norm_ranked_desc = df[normalized_columns].rank(ascending=False, method="dense", axis=1)

#         raw_ranked_asc = df[raw_numbers_columns].rank(ascending=True, method="dense", axis=1)
#         norm_ranked_asc = df[normalized_columns].rank(ascending=True, method="dense", axis=1)

#         raw_ranked_desc.reset_index(drop=True, inplace=True)
#         norm_ranked_desc.reset_index(drop=True, inplace=True)

#         raw_ranked_asc.reset_index(drop=True, inplace=True)
#         norm_ranked_asc.reset_index(drop=True, inplace=True)

#         raw_ranked_desc = raw_ranked_desc.add_suffix("_grouped_by_time_place_rank")
#         norm_ranked_desc = norm_ranked_desc.add_suffix("_grouped_by_time_place_rank")

#         raw_ranked_asc = raw_ranked_asc.add_suffix("_grouped_by_time_place_rank_reverse")
#         norm_ranked_asc = norm_ranked_asc.add_suffix("_grouped_by_time_place_rank_reverse")

#         df = pd.concat([df, raw_ranked_asc], axis=1)
#         df = pd.concat([df, norm_ranked_asc], axis=1)
#         df = pd.concat([df, raw_ranked_desc], axis=1)
#         df = pd.concat([df, norm_ranked_desc], axis=1)

#         return df

#     def _add_outlierness_to_cphi_data(self, df, outlierness_columns, id_columns):
#         const_max_out = 2

#         def outlierness(val, count, min_val, q1, q2, q3, max_val):
#             size_weight = sqrt(1 / sqrt(count))
#             if q1 == q3:
#                 if val == q2:
#                     return 0.5 * size_weight
#                 if val > q3:
#                     return 0.5 + (const_max_out - 0.5) * (val - q2) / (max_val - q2) * size_weight
#                 if val < q1:
#                     return 0.5 + (const_max_out - 0.5) * (q2 - val) / (q2 - min_val) * size_weight
#             else:
#                 if (q1 < val) and (val < q3):
#                     return min(
#                         outlierness(q1, count, min_val, q1, q2, q3, max_val),
#                         outlierness(q3, count, min_val, q1, q2, q3, max_val)
#                     ) * size_weight
#                 return abs(val - q2) / (q3 - q1) * size_weight

#         def group_outlierness(grp):
#             quantiles = grp.quantile([.25, .5, .75])
#             min_val = grp.min()
#             max_val = grp.max()
#             q1 = quantiles[0.25]
#             q2 = quantiles[0.5]
#             q3 = quantiles[0.75]
#             return grp.apply(outlierness, args=(grp.size, min_val, q1, q2, q3, max_val))

#         rank_columns = [col for col in df.columns.values if "_rank" in col]
#         numeric_columns = outlierness_columns

#         for column_name in numeric_columns:
#             #print("Crime data outliers column: " + column_name)
#             #log.debug("Generating outlyingness values for column {}".format(column_name))
#             outlierness_ct_column_name = "{}_grouped_by_crime_time_outlierness".format(column_name)
#             df[outlierness_ct_column_name] = df.groupby(["when", "when_type"])[column_name].apply(group_outlierness)

#             outlierness_ct_column_name = "{}_grouped_by_crime_place_year_outlierness".format(column_name)
#             df[outlierness_ct_column_name] = df.groupby(["where", "where_type", "year", "when_type"])[column_name].apply(group_outlierness)
#             df.loc[df['when_type'] == 'year', outlierness_ct_column_name] = np.nan

#         # Last outlierness:
#         #   fixed place and time (which crime was committed most, second most, ... in specific place at specific time)
#         raw_numbers_columns = [x for x in numeric_columns if 'normalized' not in x]
#         normalized_columns = [x for x in numeric_columns if 'normalized' in x]

#         raw_outlierness = df[raw_numbers_columns]
#         norm_outlierness = df[normalized_columns]

#         raw_outlierness.reset_index(drop=True, inplace=True)
#         norm_outlierness.reset_index(drop=True, inplace=True)

#         for i in range(len(raw_outlierness)):
#             raw_outlierness.iloc[i] = group_outlierness(raw_outlierness.iloc[i])
#             norm_outlierness.iloc[i] = group_outlierness(norm_outlierness.iloc[i])

#         raw_outlierness = raw_outlierness.add_suffix("_grouped_by_time_place_outlierness")
#         norm_outlierness = norm_outlierness.add_suffix("_grouped_by_time_place_outlierness")

#         df = pd.concat([df, raw_outlierness], axis=1)
#         df = pd.concat([df, norm_outlierness], axis=1)

#         for rank_column_name in rank_columns:
#             normal_column_name = rank_column_name.replace("_reverse", "").replace("_rank", "")
#             outlierness_rank_column_name = "{}_outlierness".format(rank_column_name)
#             outlierness_normal_column_name = "{}_outlierness".format(normal_column_name)
#             df[outlierness_rank_column_name] = df[outlierness_normal_column_name]

#         non_numeric_columns = id_columns
#         for column_name in non_numeric_columns:
#             #log.debug("Generating outlyingness values for column {}".format(column_name))
#             outlierness_column_name = "{}_outlierness".format(column_name)
#             df[outlierness_column_name] = 0.5

#         return df

#     def _add_ranks_to_comparison_data(self, df, ranked_columns):

#         pos_values = df.copy()
#         neg_values = df.copy()
#         pos_grouped = pos_values.groupby(["when1", "when2", "when_type"])
#         neg_grouped = neg_values.groupby(["when1", "when2", "when_type"])
#         for col_name in ranked_columns:
#             # Different rankings:
#             #   fixed crime and time (where specific crime was committed most, second most, ... during a specific time)
#             pos_ranked_col_name = "{}_grouped_by_crime_time_increase_rank".format(col_name)
#             neg_ranked_col_name = "{}_grouped_by_crime_time_decrease_rank".format(col_name)
#             # For each col_name, we first set the values we don't want to consider for the two cases to nan
#             pos_values.loc[pos_values[col_name] <= 0, col_name] = np.nan
#             neg_values.loc[neg_values[col_name] >= 0, col_name] = np.nan
#             # And then we generate the rank values. Note that setting the values in pos_values, and using
#             # pos_grouped for the ranking is intentional
#             df[pos_ranked_col_name] = pos_grouped[col_name].rank(ascending=False, method="dense", na_option='keep')
#             df[neg_ranked_col_name] = neg_grouped[col_name].rank(ascending=True, method="dense", na_option='keep')

#         # Last ranking:
#         #   fixed place and time (which crime was committed most, second most, ... in specific place at specific time)
#         raw_change_columns = [x for x in ranked_columns if 'normalized' not in x and 'percentage' not in x]
#         normalized_change_columns = [x for x in ranked_columns if 'normalized' in x and 'percentage' not in x]
#         percentage_change_columns = [x for x in ranked_columns if 'normalized' not in x and 'percentage' in x]
#         normalized_percentage_change_columns = [x for x in ranked_columns if 'normalized' in x and 'percentage' in x]

#         pos_raw = df[raw_change_columns].copy()
#         pos_norm = df[normalized_change_columns].copy()
#         pos_per = df[percentage_change_columns].copy()
#         pos_nope = df[normalized_percentage_change_columns].copy()

#         neg_raw = pos_raw.copy()
#         neg_norm = pos_norm.copy()
#         neg_per = pos_per.copy()
#         neg_nope = pos_nope.copy()

#         pos_raw[pos_raw <= 0] = np.nan
#         pos_norm[pos_norm <= 0] = np.nan
#         pos_per[pos_per <= 0] = np.nan
#         pos_nope[pos_nope <= 0] = np.nan

#         neg_raw[neg_raw >= 0] = np.nan
#         neg_norm[neg_norm >= 0] = np.nan
#         neg_per[neg_per >= 0] = np.nan
#         neg_nope[neg_nope >= 0] = np.nan

#         raw_change_ranked_desc = pos_raw.rank(ascending=False, method="dense", axis=1, na_option='keep')
#         normalized_change_desc = pos_norm.rank(ascending=False, method="dense", axis=1, na_option='keep')
#         percentage_change_ranked_desc = pos_per.rank(ascending=False, method="dense", axis=1, na_option='keep')
#         normalized_percentage_change_desc = pos_nope.rank(ascending=False, method="dense", axis=1, na_option='keep')

#         raw_change_ranked_asc = neg_raw.rank(ascending=True, method="dense", axis=1, na_option='keep')
#         normalized_change_asc = neg_norm.rank(ascending=True, method="dense", axis=1, na_option='keep')
#         percentage_change_ranked_asc = neg_per.rank(ascending=True, method="dense", axis=1, na_option='keep')
#         normalized_percentage_change_asc = neg_nope.rank(ascending=True, method="dense", axis=1, na_option='keep')

#         raw_change_ranked_desc = raw_change_ranked_desc.add_suffix("_grouped_by_time_place_increase_rank")
#         normalized_change_desc = normalized_change_desc.add_suffix("_grouped_by_time_place_increase_rank")
#         percentage_change_ranked_desc = percentage_change_ranked_desc.add_suffix("_grouped_by_time_place_increase_rank")
#         normalized_percentage_change_desc = normalized_percentage_change_desc.add_suffix("_grouped_by_time_place_increase_rank")

#         raw_change_ranked_asc = raw_change_ranked_asc.add_suffix("_grouped_by_time_place_decrease_rank")
#         normalized_change_asc = normalized_change_asc.add_suffix("_grouped_by_time_place_decrease_rank")
#         percentage_change_ranked_asc = percentage_change_ranked_asc.add_suffix("_grouped_by_time_place_decrease_rank")
#         normalized_percentage_change_asc = normalized_percentage_change_asc.add_suffix("_grouped_by_time_place_decrease_rank")

#         df = pd.concat([df, raw_change_ranked_desc], axis=1)
#         df = pd.concat([df, normalized_change_desc], axis=1)
#         df = pd.concat([df, percentage_change_ranked_desc], axis=1)
#         df = pd.concat([df, normalized_percentage_change_desc], axis=1)
#         df = pd.concat([df, raw_change_ranked_asc], axis=1)
#         df = pd.concat([df, normalized_change_asc], axis=1)
#         df = pd.concat([df, percentage_change_ranked_asc], axis=1)
#         df = pd.concat([df, normalized_percentage_change_asc], axis=1)

#         return df

#     def _add_outlierness_to_comparison_data(self, df, outlierness_columns, id_columns):
#         const_max_out = 2

#         def outlierness(val, count, min_val, q1, q2, q3, max_val):
#             size_weight = sqrt(1 / sqrt(count))
#             if q1 == q3:
#                 if val == q2:
#                     return 0.5 * size_weight
#                 if val > q3:
#                     return 0.5 + (const_max_out - 0.5) * (val - q2) / (max_val - q2) * size_weight
#                 if val < q1:
#                     return 0.5 + (const_max_out - 0.5) * (q2 - val) / (q2 - min_val) * size_weight
#             else:
#                 if (q1 < val) and (val < q3):
#                     return min(
#                         outlierness(q1, count, min_val, q1, q2, q3, max_val),
#                         outlierness(q3, count, min_val, q1, q2, q3, max_val)
#                     ) * size_weight
#                 return abs(val - q2) / (q3 - q1) * size_weight

#         def group_outlierness(grp):
#             quantiles = grp.quantile([.25, .5, .75])
#             min_val = grp.min()
#             max_val = grp.max()
#             q1 = quantiles[0.25]
#             q2 = quantiles[0.5]
#             q3 = quantiles[0.75]
#             return grp.apply(outlierness, args=(grp.size, min_val, q1, q2, q3, max_val))

#         rank_columns = [col for col in df.columns.values if "_rank" in col]
#         numeric_columns = outlierness_columns

#         for column_name in numeric_columns:
#             # log.debug("Generating outlyingness values for column {}".format(column_name))
#             outlierness_ct_column_name = "{}_grouped_by_crime_time_outlierness".format(column_name)
#             df[outlierness_ct_column_name] = df.groupby(["when1", "when2", "when_type"])[column_name].apply(group_outlierness)

#         # Last outlierness:
#         #   fixed place and time (which crime was committed most, second most, ... in specific place at specific time)
#         raw_change_columns = [x for x in numeric_columns if 'normalized' not in x and 'percentage' not in x]
#         normalized_change_columns = [x for x in numeric_columns if 'normalized' in x and 'percentage' not in x]
#         percentage_change_columns = [x for x in numeric_columns if 'normalized' not in x and 'percentage' in x]
#         normalized_percentage_change_columns = [x for x in numeric_columns if 'normalized' in x and 'percentage' in x]

#         raw_change_outlierness = df[raw_change_columns]
#         normalized_change_outlierness = df[normalized_change_columns]
#         percentage_change_outlierness = df[percentage_change_columns]
#         normalized_percentage_change_outlierness = df[normalized_percentage_change_columns]

#         #reset index???

#         for i in range(len(raw_change_outlierness)):
#             raw_change_outlierness.iloc[i] = group_outlierness(raw_change_outlierness.iloc[i])
#             normalized_change_outlierness.iloc[i] = group_outlierness(normalized_change_outlierness.iloc[i])
#             percentage_change_outlierness.iloc[i] = group_outlierness(percentage_change_outlierness.iloc[i])
#             normalized_percentage_change_outlierness.iloc[i] = group_outlierness(normalized_percentage_change_outlierness.iloc[i])

#         raw_change_outlierness = raw_change_outlierness.add_suffix("_grouped_by_time_place_outlierness")
#         normalized_change_outlierness = normalized_change_outlierness.add_suffix("_grouped_by_time_place_outlierness")
#         percentage_change_outlierness = percentage_change_outlierness.add_suffix("_grouped_by_time_place_outlierness")
#         normalized_percentage_change_outlierness = normalized_percentage_change_outlierness.add_suffix("_grouped_by_time_place_outlierness")

#         df = pd.concat([df, raw_change_outlierness], axis=1)
#         df = pd.concat([df, normalized_change_outlierness], axis=1)
#         df = pd.concat([df, percentage_change_outlierness], axis=1)
#         df = pd.concat([df, normalized_percentage_change_outlierness], axis=1)

#         for rank_column_name in rank_columns:
#             normal_column_name = rank_column_name.replace("_decrease_rank", "").replace("_increase_rank", "").replace("_rank", "").replace("_reverse", "")
#             outlierness_rank_column_name = "{}_outlierness".format(rank_column_name)
#             outlierness_normal_column_name = "{}_outlierness".format(normal_column_name)
#             df[outlierness_rank_column_name] = df[outlierness_normal_column_name]

#         non_numeric_columns = id_columns
#         for column_name in non_numeric_columns:
#             # log.debug("Generating outlyingness values for column {}".format(column_name))
#             outlierness_column_name = "{}_outlierness".format(column_name)
#             df[outlierness_column_name] = 0.5

#         return df


# class ConverterC:

#     def __init__(self):

#         # Assume files are available
#         self.cphi_data = pd.read_csv(os.path.join(os.path.dirname(__file__), '../data/' + "cphi.csv"))
#         # self.population_data = pd.read_csv(os.path.join(os.path.dirname(__file__), '../data/' + "population.csv"))

#         # Remove and rename
#         self.cphi_data = drop_columns(self.cphi_data, cls.keep_columns)
#         self.cphi_data = rename_columns(self.cphi_data, cls.rename_columns)
#         self._rename_entries_and_columns()

#         # Memorize some things
#         self.crime_times = list(set(self.cphi_data['when']))
#         self.population_places = list(set(self.population_data['where']))
#         self.population_times = list(set(self.population_data['when']))
#         self.crime_places = list(set(self.cphi_data['where']))
#         self._years_and_corresponding_months()


#         # Add columns
#         self.cphi_data = self._add_yearly_entries(self.cphi_data)
#         self.cphi_data = self._add_when_type_column(self.cphi_data)
#         self.cphi_data = self._add_where_type_column(self.cphi_data)
#         self.cphi_data = self._add_year_column(self.cphi_data)
#         self.cphi_data = self._add_population_column(self.cphi_data)

#         # Make broad categories df
#         self.bc_cphi_data = calculate_sums(self.cphi_data, cls.new_columns, cls.carryover_columns)

#         # Add total columns
#         self.cphi_data = total_column(self.cphi_data, cls.ignore_columns)
#         self.bc_cphi_data = total_column(self.bc_cphi_data, cls.ignore_columns)

#         # Normalize columns
#         self.cphi_data = normalize(self.cphi_data,  "population", cls.ignore_columns)
#         self.bc_cphi_data = normalize(self.bc_cphi_data, "population", cls.ignore_columns)

#         # Save data
#         self.cphi_data.sort_values(by=['where', 'when'], ascending=[True, True], inplace=True)
#         self.bc_cphi_data.sort_values(by=['where', 'when'], ascending=[True, True], inplace=True)
#         self.cphi_data.to_csv(os.path.join(os.path.dirname(__file__), '../data/' + "crime_pyn.csv"), index=False)
#         self.bc_cphi_data.to_csv(os.path.join(os.path.dirname(__file__), '../data/' + "bc_crime_pyn.csv"), index=False)

#         # Make comparison data
#         self.crime_comp_data = self._make_comparison_data(self.cphi_data, cls.ignore_columns)
#         self.bc_crime_comp_data = self._make_comparison_data(self.bc_cphi_data, cls.ignore_columns)

#         # Save comparison data
#         self.crime_comp_data.sort_values(by=['where', 'when1', 'when2'], ascending=[True, True, True], inplace=True)
#         self.bc_crime_comp_data.sort_values(by=['where', 'when1', 'when2'], ascending=[True, True, True], inplace=True)
#         self.crime_comp_data.to_csv(os.path.join(os.path.dirname(__file__), '../data/' + "crime_pyn_comp.csv"), index=False)
#         self.bc_crime_comp_data.to_csv(os.path.join(os.path.dirname(__file__), '../data/' + "bc_crime_pyn_comp.csv"), index=False)

#     '''
#     Rename some columns and values for convenience.
#     '''
#     def _rename_entries_and_columns(self):
#         self.cphi_data['where'].replace(to_replace='Total', value='fi', inplace=True)
#         self.population_data['where'].replace(to_replace='WHOLE COUNTRY', value='fi', inplace=True)
#         self.population_data['population'].replace(to_replace='..', value=np.nan, inplace=True)

#     '''
#     Add when type column.
#     '''
#     def _add_when_type_column(self, df):
#         when_types = []
#         for time in self.cphi_data['when'].values:
#             if len(time) == 4:
#                 when_types.append("year")
#             elif len(time) == 7:
#                 when_types.append("month")
#             else:
#                 when_types.append("unknown")
#         df['when_type'] = when_types
#         return df

#     '''
#     Add where type column.
#     '''
#     def _add_where_type_column(self, df):
#         where_types = []
#         for place in self.cphi_data['where']:
#             if place == "fi":
#                 where_types.append('C')
#             else:
#                 where_types.append('M')
#         df['where_type'] = where_types
#         return df

#     def _add_year_column(self, df):
#         df["year"] = list(df["when"].apply(lambda x: x[:4]))
#         return df

#     '''
#     Add population column.
#     '''
#     def _add_population_column(self, df):
#         population_column = []
#         for index, row in df.iterrows():
#             population_column.append(self._find_population(row['where'], row['when']))
#         df['population'] = population_column
#         df['population'] = df['population'].astype(float)
#         return df

#     '''
#     Finds population size for given place and time
#     '''
#     def _find_population(self, place, time):
#         quarter_time = self._transform_time(time)
#         if place not in self.population_places or quarter_time not in self.population_times:
#             return np.nan
#         return list(self.population_data[(self.population_data['when'] == quarter_time)
#                                          & (self.population_data['where'] == place)]['population'])[0]

#     '''
#     Transform yyyyMmm or yyyy time representation into yyyyQq
#     '''
#     def _transform_time(self, time):
#         # year to quarter
#         if len(time) == 4:
#             return time + "Q4"
#         # month to quarter
#         if len(time) == 7:
#             return time[:4] + "Q" + str(int(math.ceil(int(time[5:7]) / 3)))
#         # quarter to quarter
#         if len(time) == 6:
#             return time
#         # something else ?
#         return time

#     '''
#     Add yearly entries in crime data frame.
#     '''
#     def _add_yearly_entries(self, df):
#         add_these_rows = []
#         for municipality in self.crime_places:
#             for year, months in self.years_months.items():
#                 year_data = list(df[(df['where'] == municipality) & (df['when'].isin(months))].sum(numeric_only=True))
#                 year_data = [year, municipality] + year_data
#                 add_these_rows.append(year_data)
#         yearly_df = pd.DataFrame(data=add_these_rows, columns=df.columns.values)
#         df = df.append(yearly_df, ignore_index=True)
#         return df

#     '''
#     Make a dictionary where keys are years and values
#     are lists of months in those years.
#     '''
#     def _years_and_corresponding_months(self):
#         self.years_months = {}
#         for month in self.crime_times:
#             year = month[:-3]
#             if self.years_months.get(year, None) is None:
#                 self.years_months[year] = []
#             self.years_months[year].append(month)

#     '''
#     Compares how crime numbers change between consecutive years.
#     '''
#     def _make_comparison_data(self, df, ignore_columns_p):
#         comparison_columns = ['when1', 'when2', 'when_type', 'where', 'where_type']
#         change_columns1 = []
#         change_columns2 = []

#         interesting_columns = [x for x in df.columns.values if x not in ignore_columns_p]
#         for column in interesting_columns:
#             change_columns1.append(column + "_change")
#             change_columns2.append(column + "_percentage_change")

#         comparison_columns += change_columns1 + change_columns2
#         years_in_order = list(self.years_months.keys())
#         years_in_order.sort()

#         change_data = []

#         yearly_df = df[df['when'].apply(lambda x: len(x) == 4)]
#         yearly_df.sort_values(by=['where', 'when'], ascending=[True, True], inplace=True)

#         for i in range(1, len(yearly_df)):
#             row1 = yearly_df.iloc[i - 1]
#             row2 = yearly_df.iloc[i]
#             if row1['where'] != row2['where']:
#                 continue
#             datapoint = [row1['when'], row2['when'], row1['when_type'], row1['where'], row1['where_type']]
#             y1numbers = np.array(row1[interesting_columns])
#             y2numbers = np.array(row2[interesting_columns])
#             changes = y2numbers - y1numbers
#             with np.errstate(divide='ignore'):
#                 changes2 = changes / y1numbers
#                 changes2[y1numbers == 0] = np.nan
#             datapoint = datapoint + list(changes) + list(changes2)
#             change_data.append(datapoint)

#         for i in range(2, len(yearly_df)):
#             row1 = yearly_df.iloc[i - 2]
#             row2 = yearly_df.iloc[i]
#             if row1['where'] != row2['where']:
#                 continue
#             datapoint = [row1['when'], row2['when'], row1['when_type'], row1['where'], row1['where_type']]
#             y1numbers = np.array(row1[interesting_columns])
#             y2numbers = np.array(row2[interesting_columns])
#             changes = y2numbers - y1numbers
#             with np.errstate(divide='ignore'):
#                 changes2 = changes / y1numbers
#                 changes2[y1numbers == 0] = np.nan
#             datapoint = datapoint + list(changes) + list(changes2)
#             change_data.append(datapoint)

#         return pd.DataFrame(data=change_data, columns=comparison_columns)


# class TrendFinder:

#     def __init__(self):
#         self.mk_limits = {
#             5: 10,
#             6: 13,
#             7: 15,
#             8: 18,
#             9: 20,
#             10: 23
#         }
#         self.bcdf = pd.read_csv(os.path.join(os.path.dirname(__file__), '../data/bc_crime_pyn.csv'))
#         self.trend_df = self._find_trends()
#         self.trend_df.to_csv(os.path.join(os.path.dirname(__file__), '../data/bc_crime_trends.csv'), index=False)

#     def _linear_trend(self, data, order=1):
#         coeffs = np.polyfit(range(len(list(data))), list(data), order)
#         slope = coeffs[-2]
#         return float(slope)

#     # Mann-Kendall
#     def _mk_trend(self, d, c, e, m):
#         d = list(d)
#         pos = 0
#         neg = 0
#         if len(d) < 5:
#             return [np.nan, np.nan]
#         for i in range(len(d)-1):
#             for j in range(i+1, len(d)):
#                 s = d[j] - d[i]
#                 if s >= 0:
#                     pos += 1
#                 if s <= 0:
#                     neg += 1
#         sdif = abs(pos - neg)
#         limit = self.mk_limits[len(d)]
#         # Score trend
#         # Crime type weight
#         score = int(prmcnf.category_scores.get(c.split("_")[0], 3))
#         # Trend violations
#         score = score * max(pos, neg) / (pos + neg)
#         # How long trend has been going on
#         score = score * len(d)
#         # How recent the trend is
#         # score = score / (m - e + 1)
#         # How strong is the change
#         # if min(d[0], d[-1]) != 0:
#         #    score = score * max(d[0], d[-1]) / min(d[0], d[-1])
#         # elif max(d[0], d[-1]) != 0:
#         #    score = score * max(d[0], d[-1])
#         # else:
#         #    score = score
#         if sdif >= limit:
#             if pos > neg:
#                 return [1, score]
#             return [-1, -1 * score]
#         return [0, 0]

#     def _find_trends(self):
#         df = self.bcdf
#         df = df[df['when_type'] == "year"]
#         numbers_cols = [x for x in df.columns if "_normalized" in x]
#         id_cols = cls.carryover_columns
#         df = df[id_cols + numbers_cols]
#         df.dropna(axis=0, how="any", inplace=True)
#         years = sorted(df['year'].unique())
#         municipalities = sorted(df['where'].unique())
#         df["when"] = df['when'].apply(pd.to_numeric)
#         trend_cols = []
#         for numcol in numbers_cols:
#             trend_cols.append(numcol+"_linear_trend")
#             trend_cols.append(numcol + "_mk_trend")
#             trend_cols.append(numcol+"_mk_score")
#         all_columns = ['where', 'where_type', 'when1', 'when2', 'when_type'] + trend_cols
#         data = []

#         for m in municipalities:
#             for start in years:
#                 for end in years:
#                     if end <= start:
#                         continue
#                     trends = []
#                     for c in numbers_cols:
#                         values = df[(df["where"] == m) & (df["when"] >= start) & (df["when"] <= end)][c]
#                         ltr = self._linear_trend(values)
#                         my = int(years[-1])
#                         mkres = self._mk_trend(values, c, end, my)
#                         trends.append(ltr)
#                         trends.append(mkres[0])
#                         trends.append(mkres[1])
#                     mt = df[(df["where"] == m) & (df["when"] == start)].iloc[0]["where_type"]
#                     row = [m, mt, start, end, "year"] + trends
#                     data.append(row)
#         trend_df = pd.DataFrame(data, columns=all_columns)
#         return trend_df


# def drop_columns(df, keepcols):
#     return df[keepcols]


# def rename_columns(df, recols):
#     renamed_df = df
#     for key, value in recols.items():
#         renamed_df.rename(columns={key: value}, inplace=True)
#     return renamed_df


# def calculate_sums(df, newcols, carryovercols):
#     ndf = df
#     ndf = drop_columns(ndf, carryovercols)
#     for new_column in newcols.keys():
#         sum_columns = newcols.get(new_column)
#         new_values = list(df[sum_columns].sum(axis=1))
#         ndf = pd.concat([ndf, pd.DataFrame(columns=[new_column], data=new_values)], axis=1)
#     return ndf


# def total_column(df, ignorecols, name="all_total"):
#     dft = df
#     sum_columns = [x for x in df.columns.values if x not in ignorecols]
#     dft[name] = df[sum_columns].sum(axis=1)
#     return dft


# def normalize(df, normalizer, ignorecols, n=1000):
#     normalizer_column = np.array(df[normalizer])
#     normalize_columns = [x for x in df.columns.values if x not in ignorecols]
#     for normalize_col in normalize_columns:
#         normalize_column = np.array(df[normalize_col])
#         df[normalize_col + "_normalized"] = (n * normalize_column) / normalizer_column
#     return df


if __name__ == "__main__":
    run()
