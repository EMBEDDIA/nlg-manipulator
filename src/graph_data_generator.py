import logging
import urllib.request
import urllib.parse
import json
import numpy as np
import columns
import dictionary_fi
from math import cos, sqrt

log = logging.getLogger('root')


class GraphDataGenerator():

    def generate(self, registry, graph_nucleus, location):
        print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
        fact_crime = graph_nucleus._main_fact.what_type
        # which years to show
        #when1 = str(graph_nucleus._main_fact.when_1)
        #when2 = str(graph_nucleus._main_fact.when_2)
        when1 = '2010'
        when2 = '2017'
        yearstr = "2010|2011|2012|2013|2014|2015|2016|2017"
        monthstr = "01|02|03|04|05|06|07|08|09|10|11|12"
        years = yearstr.partition(when1)
        yearq = "(" + years[1] + years[2] + ")"
        print(graph_nucleus._main_fact)
        # extract crime category
        fact_crime = fact_crime.partition("_total_category")
        if fact_crime[1] == "":
            is_cat = False
            fact_crime = fact_crime[0].partition("_total")
        else:
            is_cat = True
        fact_crime = fact_crime[0] + fact_crime[1]
        if is_cat:
            fact_cat = fact_crime
        else:
            for category, crimes in columns.new_columns.items():
                if fact_crime in crimes:
                    fact_cat = category
                    break
        #print(fact_crime)
        #print(fact_cat)
        print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
        data_column = 'all_total_normalized'
        data_column = fact_cat + "_normalized"
        # find finnish name for category
        title = dictionary_fi.CRIME_TYPES[fact_cat]['pl']
        if isinstance(title, tuple):
            title = title[0]

        if location in ['Suomi', 'Finland']:
            return None

        datastore = registry.get('crime-bc-data')
        cols = [c for c in datastore.all() if c in ['where', 'when', data_column]]

        # get location population and other places with same population
        pop = datastore.query('where=={!r} and when=={!r}'.format(location, when2))['population'].iloc[0]
        popmin = 0.9 * pop
        popmax = 1.1 * pop
        similar_places = list(set(datastore.query('when=={!r} and population<{} and population>{}'.format(when2, popmax, popmin))['where']))
        similar_places.remove(location)

        # get monthly category data
        location_df = datastore.query('where=={!r} and when_type=={!r} and where_type=="M"'.format(location, 'month'))[cols]
        elsewhere_df = datastore.query('where!={!r} and when_type=={!r} and where_type=="M"'.format(location, 'month'))[cols]
        similar_places_df = elsewhere_df[elsewhere_df['where'].isin(similar_places)]

        location_df = location_df[location_df['when'].str.contains(yearq)]
        elsewhere_df = elsewhere_df[elsewhere_df['when'].str.contains(yearq)]
        similar_places_df = similar_places_df[similar_places_df['when'].str.contains(yearq)]

        # Drop infs & nans, group by 'when', get means
        location_df = location_df.replace([np.inf, -np.inf], np.nan) \
            .dropna(how="any") \
            .groupby(['when'], as_index=False) \
            .mean()

        elsewhere_df = elsewhere_df.replace([np.inf, -np.inf], np.nan) \
            .dropna(how="any") \
            .groupby(['when'], as_index=False) \
            .mean()

        similar_places_df = similar_places_df.replace([np.inf, -np.inf], np.nan) \
            .dropna(how="any") \
            .groupby(['when'], as_index=False) \
            .mean()

        location_df = location_df[location_df['when'].str.contains(yearq)]
        elsewhere_df = elsewhere_df[elsewhere_df['when'].str.contains(yearq)]
        similar_places_df = similar_places_df[similar_places_df['when'].str.contains(yearq)]

        # get yearly month
        monthlist = monthstr.split('|')
        subgraph_location = {}
        subgraph_similar = {}
        subgraph_all_others = {}
        for m in monthlist:
            subgraph_location[m] = list(location_df[location_df['when'].str.endswith(m)][data_column])
            subgraph_similar[m] = list(elsewhere_df[elsewhere_df['when'].str.endswith(m)][data_column])
            subgraph_all_others[m] = list(similar_places_df[similar_places_df['when'].str.endswith(m)][data_column])

        # Should be same columns in both dataframes
        labels = list(location_df['when'])
        datasets = [
            {
                'label': location,
                'data': list(location_df[data_column]),
                'subgraph_data': subgraph_location,
                'backgroundColor': 'rgba(205, 170, 152, 0.2)',
                'borderColor': 'rgba(205, 170, 152, 1)',
            },
            {
                'label': 'Muiden kuntien keskiarvo ',
                'data': list(elsewhere_df[data_column]),
                'subgraph_data': subgraph_all_others,
                'backgroundColor': 'rgba(151, 187, 205, 0.2)',
                'borderColor': 'rgba(151, 187, 205, 1)',
            },
            {
                'label': 'Samanlaisten kuntien keskiarvo ',
                'data': list(similar_places_df[data_column]),
                'subgraph_data': subgraph_similar,
                'backgroundColor': 'rgba(156, 230, 160, 0.2)',
                'borderColor': 'rgba(156, 230, 160, 1)',
            }
        ]

        return json.dumps({
            'labels': labels,
            'datasets': datasets,
            'title' : title[0].capitalize() + title[1:]
        });

    def _get_graph(self, labels, datasets):
        return """
            <canvas id="chart" width="500" height="500"></canvas>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.22.1/moment.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.7.2/Chart.min.js"></script>
            <script>
                var chart = new Chart(
                    document.getElementById('chart'), 
                    {{
                        type: 'line',
                        data: {{
                            labels: {labels},
                            datasets: {datasets}
                        }},
                        options: {{
                            title: {{
                                display: true,
                                text: 'Rikoksia tuhatta asukasta kohden'
                            }}
                        }}
                    }}
                )
            </script>
        """.format(labels=labels, datasets=datasets)
