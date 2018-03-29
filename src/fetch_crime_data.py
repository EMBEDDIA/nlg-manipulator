from opendata.px_reader import *
from opendata.statfi_px_api import *
import pandas as pd
import numpy as np
from math import sqrt
import math
import os.path
from timeit import default_timer as timer

def run():
    # Download list of available PX files
    all_px = list_available_px()
    
    # Find Crime stats and Population stats
    wanted_px = [px for px in all_px if 'statfin_rpk_pxt_001.px' in str(px) or 'statfin_vamuu_pxt_003.px' in str(px)]

    # Download the data
    download_px(wanted_px, target_dir='..')

    print('Data dir is', os.path.join(os.path.dirname(__file__), '../data/'))
    os.makedirs(os.path.join(os.path.dirname(__file__), '../data/'), exist_ok=True)

    # Store and store population data
    df = Px('../database/StatFin/vrm/vamuu/statfin_vamuu_pxt_003.px', language='en').pd_dataframe()
    df = flatten(df)
    df = pythonify_column_names(df)
    df.rename(columns={
        'level_0': 'when', 
        'level_1': 'where', 
        'both_sexes_age_groups_total_premilinary_population': 'population'}
        , inplace=True)
    df = df[['when', 'where', 'population']]
    df.replace(['"-"', '".."'], 0, inplace=True)
    df.to_csv(os.path.join(os.path.dirname(__file__), '../data/population.csv'))

    # flatten and store crime statistics
    df = Px("../database/StatFin/oik/rpk/statfin_rpk_pxt_001.px", language='en').pd_dataframe().transpose()
    df = flatten(df, stacked_cols=[0])
    df = pythonify_column_names(df)
    df.rename(columns={'level_0': 'when', 'level_1': 'where'}, inplace=True)
    df.replace(['"-"', '".."'], 0, inplace=True)
    df.to_csv(os.path.join(os.path.dirname(__file__), '../data/crime.csv'))

    print(os.path.join(os.path.dirname(__file__), '../data/crime.csv'))

    print('Converter')
    ConverterC()

    print('Importer')
    ImporterC()

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
        self.cdc.to_csv(os.path.join(os.path.dirname(__file__), '../data/' + prefix + "pyn_crime_y12_comparison_ranks_outliers.csv"), index=False)
        #'''

    def _load_data(self, prefix):
        self.crime_data = pd.read_csv(os.path.join(os.path.dirname(__file__), '../data/' + prefix + "pyn_crime.csv"))
        self.comparison_data = pd.read_csv(os.path.join(os.path.dirname(__file__), '../data/' +prefix + "pyn_crime_y12_comparison.csv"))
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

class ConverterC:

    def __init__(self, fake=False):

        if fake:
            prefix = "fake_"
        else:
            prefix = ""
        time_read_files = timer()

        self.crime_data = pd.read_csv(os.path.join(os.path.dirname(__file__), '../data/' + prefix + "crime.csv"))
        self.population_data = pd.read_csv(os.path.join(os.path.dirname(__file__), '../data/' + "population.csv"))

        time_cleaning = timer()

        self._rename_entries_and_columns()
        self._remove_unneeded_columns_by_column_name()

        self.crimes = list(self.crime_data.columns.values)[2:]
        self.crime_places = list(set(self.crime_data['where']))
        self.crime_times = list(set(self.crime_data['when']))
        self.crime_places.sort()
        self.crime_times.sort()

        self.population_places = list(set(self.population_data['where']))
        self.population_times = list(set(self.population_data['when']))
        self.population_places.sort()
        self.population_times.sort()

        self._years_and_corresponding_months()

        time_crime = timer()

        #'''Crime data package
        self._add_yearly_entries()
        self._add_population_column()
        self._add_when_type_column()
        self._add_where_type_column()
        self._add_normalized_crime_numbers()
        self._reorder_crime_data_columns()
        self.crime_data.sort_values(by=['where', 'when'], ascending=[True, True], inplace=True)
        self.crime_data.to_csv(os.path.join(os.path.dirname(__file__), '../data/' + prefix + "pyn_crime.csv"), index=False)
        #'''

        '''Read this if not making new crime data
        self.crime_data = pd.read_csv("pyn_crime.csv")
        #'''

        time_comparison1 = timer()

        #'''Comparison data package 1
        self._make_comparison_data1()
        self._reorder_comparison_data()
        self.crime_change_data.sort_values(by=['where', 'when1', 'when2'], ascending=[True, True, True], inplace=True)
        self.crime_change_data.to_csv(os.path.join(os.path.dirname(__file__), '../data/' + prefix + 'pyn_crime_y12_comparison.csv'), index=False)
        #'''

        time_comparison2 = timer()

        '''Comparison data package 2
        self._make_comparison_data2()
        self._reorder_comparison_data2()
        self.crime_change_data2.sort_values(by=['where', 'when1', 'when2'], ascending=[True, True, True], inplace=True)
        self.crime_change_data2.to_csv('a_crime_comparison2.csv', index=False)
        #'''

        time_end = timer()

        print('Crime data: ' + str(time_comparison1 - time_crime))
        print('Comparison: ' + str(time_comparison2 - time_comparison1))

    '''
    Rename some columns and values for convenience.
    '''
    def _rename_entries_and_columns(self):
        self.crime_data['where'].replace(to_replace='Total', value='FI', inplace=True)
        self.population_data['where'].replace(to_replace='WHOLE COUNTRY', value='FI', inplace=True)
        self.population_data['population'].replace(to_replace='..', value=np.nan, inplace=True)

    '''
    Remove unwanted columns from crime data frame based on index.
    '''
    def _remove_unneeded_columns(self):
        number_of_columns = len(self.crime_data.columns.values)
        keep_these = [x for x in range(1, number_of_columns) if (x > 0 & x < 3) or (x + 2) % 5 == 0]
        self.crime_data = self.crime_data[self.crime_data.columns[keep_these]]

    '''
    Remove unwanted columns from crime data frame based on column name.
    '''
    def _remove_unneeded_columns_by_column_name(self):
        needed_columns = []
        for column in self.crime_data.columns.values:
            if column.endswith('when') or column.endswith('where') or column.endswith('_all_offences'):
                needed_columns.append(column)
        self.crime_data = self.crime_data[needed_columns]

    '''
    Make a dictionary where keys are years and values
    are lists of months in those years.
    '''
    def _years_and_corresponding_months(self):
        self.years_months = {}
        for month in self.crime_times:
            year = month[:-3]
            if self.years_months.get(year, None) is None:
                self.years_months[year] = []
            self.years_months[year].append(month)

    '''
    Add yearly entries in crime data frame.
    '''
    def _add_yearly_entries(self):
        add_these_rows = []
        for municipality in self.crime_places:
            for year, months in self.years_months.items():
                year_data = list(self.crime_data[(self.crime_data['where'] == municipality)
                                                 & (self.crime_data['when'].isin(months))].sum(numeric_only=True))
                year_data = [year, municipality] + year_data
                add_these_rows.append(year_data)
        yearly_df = pd.DataFrame(data=add_these_rows, columns=self.crime_data.columns.values)
        self.crime_data = self.crime_data.append(yearly_df, ignore_index=True)

    '''
    Add population column.
    '''
    def _add_population_column(self):
        population_column =[]
        for index, row in self.crime_data.iterrows():
            population_column.append(self._find_population(row['where'], row['when']))
        self.crime_data['population'] = population_column
        self.crime_data['population'] = self.crime_data['population'].astype(float)

    '''
    Add when type column.
    '''
    def _add_when_type_column(self):
        when_types = []
        for time in self.crime_data['when'].values:
            if len(time) == 4:
                when_types.append("year")
            elif len(time) == 7:
                when_types.append("month")
            else:
                when_types.append("unknown")
        self.crime_data['when_type'] = when_types

    '''
    Add where type column.
    '''
    def _add_where_type_column(self):
        where_types = []
        for place in self.crime_data['where']:
            if place == "FI":
                where_types.append('C')
            else:
                where_types.append('M')
        self.crime_data['where_type'] = where_types

    '''
    Add normalized columns (how many times crime was committed
    for every n people).
    '''
    def _add_normalized_crime_numbers(self, n=1000):
        population_column = np.array(self.crime_data['population'])
        for crime in self.crimes:
            crime_column = np.array(self.crime_data[crime])
            self.crime_data[crime+"_normalized"] = (n * crime_column) / population_column

    '''
    Finds population size for given place and time
    '''
    def _find_population(self, place, time):
        quarter_time = self._transform_time(time)
        if place not in self.population_places or quarter_time not in self.population_times:
            return np.nan
        return list(self.population_data[(self.population_data['when'] == quarter_time)
                                    & (self.population_data['where'] == place)]['population'])[0]

    '''
    Transform yyyyMmm or yyyy time representation into yyyyQq
    '''
    def _transform_time(self, time):
        # year to quarter
        if len(time) == 4:
            return time + "Q4"
        # month to quarter
        if len(time) == 7:
            return time[:4] + "Q" + str(int(math.ceil(int(time[5:7]) / 3)))
        # quarter to quarter
        if len(time) == 6:
            return time
        # something else ?
        return time

    def _reorder_crime_data_columns(self):
        column_names = list(self.crime_data.columns.values)
        first_columns = ['when', 'when_type', 'where', 'where_type', 'population']
        last_columns = [name for name in column_names if name not in first_columns]
        last_columns.sort()
        self.crime_data = self.crime_data[first_columns+last_columns]

    def _reorder_comparison_data(self):
        start = list(self.crime_change_data.columns.values[:5])
        end = list(self.crime_change_data.columns.values[5:])
        end.sort()
        self.crime_change_data = self.crime_change_data[start + end]

    def _reorder_comparison_data2(self):
        start = list(self.crime_change_data2.columns.values[:5])
        end = list(self.crime_change_data2.columns.values[5:])
        end.sort()
        self.crime_change_data2 = self.crime_change_data2[start + end]

    '''
    Compares how crime numbers change between consecutive years.
    '''
    def _make_comparison_data1(self):
        comparison_columns = ['when1', 'when2', 'when_type', 'where', 'where_type']
        change_columns1 = []
        change_columns2 = []

        for column in self.crime_data.columns.values[4:]:
            change_columns1.append(column + "_change")
            change_columns2.append(column + "_percentage_change")

        comparison_columns += change_columns1 + change_columns2
        years_in_order = list(self.years_months.keys())
        years_in_order.sort()

        change_data = []

        yearly_df = self.crime_data[self.crime_data['when'].apply(lambda x: len(x) == 4)]
        yearly_df.sort_values(by=['where', 'when'], ascending=[True, True], inplace=True)

        for i in range(1, len(yearly_df)):
            row1 = yearly_df.iloc[i-1]
            row2 = yearly_df.iloc[i]
            if row1['where'] != row2['where']:
                continue
            datapoint = [row1['when'], row2['when'], row1['when_type'], row1['where'], row1['where_type']]
            y1numbers = np.array(row1[self.crime_data.columns.values[4:]])
            y2numbers = np.array(row2[self.crime_data.columns.values[4:]])
            changes = y2numbers - y1numbers
            with np.errstate(divide='ignore'):
                changes2 = changes / y1numbers
                changes2[y1numbers == 0] = np.nan
            datapoint = datapoint + list(changes) + list(changes2)
            change_data.append(datapoint)

        for i in range(2, len(yearly_df)):
            row1 = yearly_df.iloc[i-2]
            row2 = yearly_df.iloc[i]
            if row1['where'] != row2['where']:
                continue
            datapoint = [row1['when'], row2['when'], row1['when_type'], row1['where'], row1['where_type']]
            y1numbers = np.array(row1[self.crime_data.columns.values[4:]])
            y2numbers = np.array(row2[self.crime_data.columns.values[4:]])
            changes = y2numbers - y1numbers
            with np.errstate(divide='ignore'):
                changes2 = changes / y1numbers
                changes2[y1numbers == 0] = np.nan
            datapoint = datapoint + list(changes) + list(changes2)
            change_data.append(datapoint)

        '''    
        for i in range(1, len(years_in_order)):
            for place in self.crime_places:
                y1 = years_in_order[i-1]
                y2 = years_in_order[i]
                row1 = self.crime_data[(self.crime_data['when'] == y1) & (self.crime_data['where'] == place)]
                row2 = self.crime_data[(self.crime_data['when'] == y2) & (self.crime_data['where'] == place)]
                datapoint = [y1, y2, row1['when_type'].values[0], place, row1['where_type'].values[0]]
                y1numbers = np.array(row1[self.crime_data.columns.values[4:]])[0]
                y2numbers = np.array(row2[self.crime_data.columns.values[4:]])[0]
                changes = y2numbers - y1numbers
                with np.errstate(divide='ignore'):
                    changes2 = changes / y1numbers
                    changes2[y1numbers == 0] = np.nan
                datapoint = datapoint + list(changes) + list(changes2)
                change_data.append(datapoint)

        for i in range(2, len(years_in_order)):
            for place in self.crime_places:
                y1 = years_in_order[i-2]
                y2 = years_in_order[i]
                row1 = self.crime_data[(self.crime_data['when'] == y1) & (self.crime_data['where'] == place)]
                row2 = self.crime_data[(self.crime_data['when'] == y2) & (self.crime_data['where'] == place)]
                datapoint = [y1, y2, row1['when_type'].values[0], place, row1['where_type'].values[0]]
                y1numbers = np.array(row1[self.crime_data.columns.values[4:]])[0]
                y2numbers = np.array(row2[self.crime_data.columns.values[4:]])[0]
                changes = y2numbers - y1numbers
                with np.errstate(divide='ignore'):
                    changes2 = changes / y1numbers
                    changes2[y1numbers == 0] = np.nan
                datapoint = datapoint + list(changes) + list(changes2)
                change_data.append(datapoint)
        #'''
        self.crime_change_data = pd.DataFrame(data=change_data, columns=comparison_columns)

    '''
    Changes between same months of consecutive years
    '''
    def _make_comparison_data2(self):
        comparison_columns = ['when1', 'when2', 'when_type', 'where', 'where_type']
        change_columns1 = []
        change_columns2 = []

        for column in self.crime_data.columns.values[4:]:
            change_columns1.append(column + "_change")
            change_columns2.append(column + "_percentage_change")

        comparison_columns += change_columns1 + change_columns2

        change_data = []

        for i in range(12, len(self.crime_times)):
            for place in self.crime_places:
                y1 = self.crime_times[i - 12]
                y2 = self.crime_times[i]
                row1 = self.crime_data[(self.crime_data['when'] == y1) & (self.crime_data['where'] == place)]
                row2 = self.crime_data[(self.crime_data['when'] == y2) & (self.crime_data['where'] == place)]
                datapoint = [y1, y2, row1['when_type'].values[0], place, row1['where_type'].values[0]]
                y1numbers = np.array(row1[self.crime_data.columns.values[4:]])[0]
                y2numbers = np.array(row2[self.crime_data.columns.values[4:]])[0]
                changes = y2numbers - y1numbers
                with np.errstate(divide='ignore'):
                    changes2 = changes / y1numbers
                    changes2[(y1numbers == 0) | (y1numbers == np.nan)] = np.nan
                datapoint = datapoint + list(changes) + list(changes2)
                change_data.append(datapoint)
        self.crime_change_data2 = pd.DataFrame(data=change_data, columns=comparison_columns)

if __name__ == "__main__":
    run()