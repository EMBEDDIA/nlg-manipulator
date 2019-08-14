# News generation from EU data

Work-in-progress.

## Data and preparation

Data that is used is collected from [Eurostat Database](https://ec.europa.eu/eurostat/data/database).

Chosen datasets are flattened to two dimensional Pandas DataFrames and combined. The subDataFrames have the following columns: `'when', 'when_type', 'where', 'where_type'` and columns for the actual values. The value column names begin with an indicator to the original dataset.

## Pipeline

#### Message generation

Messages are built from the DataFrame that is prepared by the `fetch_eu_data.py` file. A message includes a fact that has the following fields: `where, where_type, when_1, when_2, when_type, what (value of the value column), what_type (name of the value column), outlierness (from outlierness column)` 

#### Importance allocation

<< to be decided >>

#### Document planning

Done by the NLG Core.

#### Templates

<< to be decided >>

#### Aggregation

Done by the NLG Core.

#### Slot realization

<< to be decided >>

#### Entity name resolving

<< to be decided >>

## API

#### Get a random news article:
`GET /api/random`

#### Get a news article for a specific location 
`GET /api/news`

Possible query parameters:
`where`

Example:
`GET /api/news?where=91`
