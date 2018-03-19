import pandas as pd
import math
import numpy as np
import os.path
from timeit import default_timer as timer

# 120s cr + comp1


class ConverterC:

    def __init__(self, fake=False):

        if fake:
            prefix = "fake_"
        else:
            prefix = ""
        time_read_files = timer()

        self.crime_data = pd.read_csv(prefix + "crime.csv")
        self.population_data = pd.read_csv("population.csv", skiprows=1, encoding="ISO-8859-1", sep=';')

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
        self.crime_data.to_csv(prefix + "pyn_crime.csv", index=False)
        #'''

        '''Read this if not making new crime data
        self.crime_data = pd.read_csv("pyn_crime.csv")
        #'''

        time_comparison1 = timer()

        #'''Comparison data package 1
        self._make_comparison_data1()
        self._reorder_comparison_data()
        self.crime_change_data.sort_values(by=['where', 'when1', 'when2'], ascending=[True, True, True], inplace=True)
        self.crime_change_data.to_csv(prefix + 'pyn_crime_y12_comparison.csv', index=False)
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
        self.population_data.columns = ["when", "where", "population"]
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


