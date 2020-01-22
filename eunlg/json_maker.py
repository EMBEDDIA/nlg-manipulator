import pandas as pd
import numpy as np
from operator import itemgetter
import matplotlib.pyplot as plt
import json
import os
import columns as cls

class GraphDataGetter:

    def __init__(self):
        self.crime_data = pd.read_csv(os.path.join(os.path.dirname(__file__), "../data/crime_pyn_ranks_outliers.csv"))
        self.comparison_data = pd.read_csv(os.path.join(os.path.dirname(__file__), "../data/crime_pyn_comp_ranks_outliers.csv"))
        self.bc_crime_data = pd.read_csv(os.path.join(os.path.dirname(__file__), "../data/bc_crime_pyn_ranks_outliers.csv"))
        self.bc_comparison_data = pd.read_csv(os.path.join(os.path.dirname(__file__), "../data/bc_crime_pyn_comp_ranks_outliers.csv"))
        #self.bc = pd.read_csv(os.path.join(os.path.dirname(__file__), "column/new_columns_table.csv"))
        self.bc = cls.new_columns


    def inc_dec_crimes(self, place, year, comp=1, context=5, broad_categories=True, percentage=True,
                       normalized=True, mplot=False, category_names=None):
        if category_names is None:
            category_names = []
        if broad_categories:
            compdata = self.bc_comparison_data
            data = self.bc_crime_data
            used_columns = list(data.columns.values)
        else:
            compdata = self.comparison_data
            data = self.crime_data
            used_columns = list(data.columns.values)
            if len(category_names) > 0:
                used_columns = []
                for col in self.bc.keys():
                    if col not in category_names:
                        continue
                    uc = list(self.bc[col])
                    used_columns = used_columns + uc

        comp_year = year - comp

        df = compdata[(compdata["when1"] == comp_year) & (compdata["when2"] == year) & (compdata["where"] == place)]

        if percentage:
            if normalized:
                rank_cols = [x for x in compdata.columns.values if
                             x.endswith("_normalized_percentage_change_grouped_by_time_place_rank")]
            else:
                rank_cols = [x for x in compdata.columns.values if
                             (x.endswith("_percentage_change_grouped_by_time_place_rank") and not x.endswith(
                                 "_normalized_percentage_change_grouped_by_time_place_rank"))]
        else:
            if normalized:
                rank_cols = [x for x in compdata.columns.values if
                             x.endswith("_normalized_change_grouped_by_time_place_rank")]
            else:
                rank_cols = [x for x in compdata.columns.values if
                             (x.endswith("_change_grouped_by_time_place_rank") and not x.endswith(
                                 "_normalized_change_grouped_by_time_place_rank") and not x.endswith(
                                 "_percentage_change_grouped_by_time_place_rank"))]

        ranks = list(df[rank_cols].iloc[0])
        #print(df)
        if percentage:
            if normalized:
                ccolumns = [x.replace("_normalized_percentage_change_grouped_by_time_place_rank", "") for x in
                            rank_cols]
            else:
                ccolumns = [x.replace("_percentage_change_grouped_by_time_place_rank", "") for x in
                            rank_cols]
        else:
            if normalized:
                ccolumns = [x.replace("_normalized_change_grouped_by_time_place_rank", "") for x in rank_cols]
            else:
                ccolumns = [x.replace("_change_grouped_by_time_place_rank", "") for x in rank_cols]

        ranks_columns = zip(ranks, ccolumns)
        crimes = len(ccolumns)
        ranks_columns = [x for x in ranks_columns if not np.isnan(x[0]) and x[1] in used_columns]
        sorted_ranks_columns = sorted(ranks_columns, key=itemgetter(0))
        for item in sorted_ranks_columns:
            print(item)

        most_inc = sorted_ranks_columns[0][1]
        most_dec = sorted_ranks_columns[-1][1]
        years = list(range(year - context + 1, year + 1))

        ddf = data[(data["year"].isin(years)) & (data["where"] == place)]
        if mplot:
            ddf = ddf[ddf['when'].apply(lambda x: len(str(x)) == 7)]
        else:
            ddf = ddf[ddf['when'].apply(lambda x: len(str(x)) == 4)]
        ddf.sort_values(by=['when'], ascending=[True], inplace=True)

        most_inc_monthly_values = [float(round(x, 1)) for x in list(ddf[most_inc])]
        most_dec_monthly_values = [float(round(x, 1)) for x in list(ddf[most_dec])]
        #everything no just chosen categories
        avg_monthly_values = list(ddf['all_total'])
        avg_monthly_values = [float(round(x/crimes, 1)) for x in avg_monthly_values]
        '''
        plt.plot(avg_monthly_values, label="average")
        plt.plot(most_inc_monthly_values, label="increased most")
        plt.plot(most_dec_monthly_values, label="decreased most")
        plt.legend()
        plt.show()
        '''
        jd = {"inc_name": str(most_inc), "dec_name": str(most_dec), "inc_val": list(most_inc_monthly_values),
              "dec_val": list(most_dec_monthly_values), "avg_val": list(avg_monthly_values)}
        print(json.dumps(jd, sort_keys=False, indent=4, separators=(',', ':')))
        #print(jd)
        return jd

    def numbers(self, place, year, broad_categories=True, category_names=None):
        if category_names is None:
            category_names = []
        if broad_categories:
            data = self.bc_crime_data
            used_columns = list(data.columns.values)
        else:
            data = self.crime_data
            used_columns = list(data.columns.values)
            if len(category_names) > 0:
                used_columns = []
                for col in self.bc.keys():
                    if col not in category_names:
                        continue
                    uc = list(self.bc[col])
                    used_columns = used_columns + uc
        year = str(year)
        df = data[(data['where'] == place) & (data['when'] == year)]
        cols = list(df.columns.values)
        cols = [x for x in cols if (x.endswith("_total") or x.endswith("_category")) and not x.startswith("all")]
        values = [float(x) for x in list(df[cols].iloc[0])]
        colval = zip(cols, values)
        colval = [x for x in colval if not np.isnan(x[1]) and x[0] in used_columns]
        colval = sorted(colval, key=itemgetter(1))
        #print(values)
        jd = {}
        plot_vals = []
        plot_cols = []
        for pair in colval:
            jd[pair[0]] = pair[1]
            plot_vals.append(pair[1])
            plot_cols.append(pair[0])
            #print(pair)
        '''
        plt.pie(plot_vals, labels=plot_cols)
        plt.show()
        '''
        print(json.dumps(jd, sort_keys=False, indent=4, separators=(',', ':')))
        return jd
