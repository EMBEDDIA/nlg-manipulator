import itertools
import os.path
from math import sqrt

import numpy as np
import pandas as pd

from country_clusteriser import CountryClusteriser


def compare_to_us(df, compare_columns):

    us_df = df.loc[df["where"] == "US"]
    df = df.drop(us_df.index)
    df = pd.concat([us_df, df])

    grouped_cphi_time = df.groupby("when")

    for col_name in compare_columns:
        compared_col_name = "{}_grouped_by_time_comp_us".format(col_name)
        grouped = grouped_cphi_time[col_name]
        df[compared_col_name] = df[col_name] - grouped.transform("first")

    return df


def compare_to_eu(df, compare_columns):

    eu_df = df.loc[df["where"] == "EU"]
    df = df.drop(eu_df.index)
    df = pd.concat([eu_df, df])

    grouped_cphi_time = df.groupby("when")

    for col_name in compare_columns:
        compared_col_name = "{}_grouped_by_time_comp_eu".format(col_name)
        grouped = grouped_cphi_time[col_name]
        df[compared_col_name] = df[col_name] - grouped.transform("first")

    return df


def compare_to_similar(df, cluster_df, compare_columns):

    df = df.merge(cluster_df, on="where")
    grouped_b_time_and_cluster = df.groupby(["when", "cluster"])

    for col_name in compare_columns:
        compared_col_name = "{}_grouped_by_time_comp_similar".format(col_name)
        grouped = grouped_b_time_and_cluster[col_name]
        df[compared_col_name] = df[col_name] - grouped.transform("mean")

    df = df.drop("cluster", axis=1)

    return df


def rank_df(df, rank_columns):
    grouped_time = df.groupby(["when", "when_type"])
    # grouped_cphi_place = df.groupby(["where", "where_type", "when", "when_type"])

    for col_name in rank_columns:
        ranked_col_name = "{}_grouped_by_time_rank".format(col_name)
        reverse_ranked_col_name = "{}_reverse".format(ranked_col_name)
        grouped = grouped_time[col_name]
        df[ranked_col_name] = grouped.rank(ascending=False, method="dense", na_option="keep")
        df[reverse_ranked_col_name] = grouped.rank(ascending=True, method="dense", na_option="keep")
    return df


def add_outlierness_to_data(df, outlierness_columns, id_columns):

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
                return (
                    min(
                        outlierness(q1, count, min_val, q1, q2, q3, max_val),
                        outlierness(q3, count, min_val, q1, q2, q3, max_val),
                    )
                    * size_weight
                )
            return abs(val - q2) / (q3 - q1) * size_weight

    def group_outlierness(grp):
        quantiles = grp.quantile([0.25, 0.5, 0.75])
        min_val = grp.min()
        max_val = grp.max()
        q1 = quantiles[0.25]
        q2 = quantiles[0.5]
        q3 = quantiles[0.75]
        return grp.apply(outlierness, args=(grp.size, min_val, q1, q2, q3, max_val))

    rank_columns = [col for col in df.columns.values if "_rank" in col]
    numeric_columns = outlierness_columns

    for column_name in numeric_columns:
        outlierness_ct_column_name = "{}_grouped_by_time_outlierness".format(column_name)
        df[outlierness_ct_column_name] = df.groupby(["when", "when_type"])[column_name].apply(group_outlierness)

    # Last outlierness:
    #   fixed place and time (which crime was committed most, second most, ... in specific place at specific time)
    raw_numbers_columns = [x for x in numeric_columns if "normalized" not in x]
    normalized_columns = [x for x in numeric_columns if "normalized" in x]

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
        # log.debug("Generating outlyingness values for column {}".format(column_name))
        outlierness_column_name = "{}_outlierness".format(column_name)
        df[outlierness_column_name] = 0.5

    return df


def flatten_cphi(df):
    """
    Flatten a data frame so that each field contains a single value.
    """
    # Replace every underscore in DataFrame
    for column in df.columns:
        df[column] = df[column].str.replace("_", "-")
    new_df = pd.DataFrame()
    names = list(df.columns)

    new_columns = names.pop(0)

    initial_content = []
    values = df.values.tolist()
    values = [value[1:] for value in values]
    values = list(itertools.chain.from_iterable(values))
    values_n_flags = pd.DataFrame(values)[0].str.split(" ", expand=True)
    values_n_flags = values_n_flags.rename(columns={0: "value", 1: "flag"})

    for line in df[new_columns]:
        for when in names:
            initial_content.append((",").join([line, when]))
    new_columns = (",").join([new_columns, "when"])
    new_df[new_columns] = initial_content

    columns = new_columns.split(",")
    new_df = new_df[new_columns].str.split(",", expand=True)
    new_df = new_df.rename(columns=dict(zip(list(new_df.columns), columns)))
    new_df = new_df.rename(columns={"geo\\time": "where"})

    new_df[["value", "flag"]] = values_n_flags

    new_df = pd.pivot_table(
        new_df, index=["where", "when"], columns=["unit", "indic"], values="value", aggfunc="first",
    )
    new_df.reset_index(level=["where", "when"], inplace=True)
    new_df.columns = new_df.columns.to_flat_index()
    new_df.columns = [("cphi_" + column[0] + "_" + column[1]).lower() for column in new_df.columns]
    new_df.rename(columns={"cphi_where_": "where", "cphi_when_": "when"}, inplace=True)

    new_df = new_df.replace(to_replace=":", value=np.nan)

    data = [pd.to_numeric(new_df[s], errors="ignore") for s in new_df.columns]
    new_df = pd.concat(data, axis=1, keys=[s.name for s in data])

    # Add when_type and where_type TODO: for example the euro area is now labeled as a country
    where_type = ["C"] * new_df.shape[0]
    when_type = ["month"] * new_df.shape[0]

    new_df["where_type"] = where_type
    new_df["when_type"] = when_type

    # Remove redundant spaces
    new_df["when"] = [when.strip(" ") for when in new_df["when"]]

    return new_df


def flatten_health(df):
    """
    Flatten a data frame so that each field contains a single value.
    """
    # Replace every underscore in DataFrame
    for column in df.columns:
        df[column] = df[column].str.replace("_", "-")
    new_df = pd.DataFrame()
    names = list(df.columns)

    new_columns = names.pop(0)

    initial_content = []
    values = df.values.tolist()
    values = [value[1:] for value in values]
    values = list(itertools.chain.from_iterable(values))
    values_n_flags = pd.DataFrame(values)[0].str.split(" ", expand=True)
    values_n_flags = values_n_flags.rename(columns={0: "value", 1: "flag"})

    for line in df[new_columns]:
        for when in names:
            initial_content.append((",").join([line, when]))
    new_columns = (",").join([new_columns, "when"])
    new_df[new_columns] = initial_content

    columns = new_columns.split(",")
    new_df = new_df[new_columns].str.split(",", expand=True)
    new_df = new_df.rename(columns=dict(zip(list(new_df.columns), columns)))
    new_df = new_df.rename(columns={"geo\\TIME_PERIOD": "where"})

    new_df[["value", "flag"]] = values_n_flags
    new_df = pd.pivot_table(
        new_df, index=["where", "when"], columns=["unit", "icha11_hf"], values="value", aggfunc="first",
    )
    new_df.reset_index(level=["where", "when"], inplace=True)
    new_df.columns = new_df.columns.to_flat_index()
    new_df.columns = [("health_" + column[0] + "_" + column[1]).lower() for column in new_df.columns]
    new_df.rename(columns={"health_where_": "where", "health_when_": "when"}, inplace=True)
    new_df = new_df.replace(to_replace=":", value=np.nan)

    data = [pd.to_numeric(new_df[s], errors="ignore") for s in new_df.columns]
    new_df = pd.concat(data, axis=1, keys=[s.name for s in data])

    # Add when_type and where_type TODO: for example the euro area is now labeled as a country
    where_type = ["C"] * new_df.shape[0]
    when_type = ["year"] * new_df.shape[0]

    new_df["where_type"] = where_type
    new_df["when_type"] = when_type

    return new_df


def flatten_income(df):
    """
    Flatten a data frame so that each field contains a single value.
    """
    # Replace every underscore in DataFrame
    for column in df.columns:
        df[column] = df[column].str.replace("_", "-")
    new_df = pd.DataFrame()
    names = list(df.columns)
    new_columns = names.pop(0)

    initial_content = []
    values = df.values.tolist()
    values = [value[1:] for value in values]
    values = list(itertools.chain.from_iterable(values))
    values_n_flags = pd.DataFrame(values)[0].str.split(" ", expand=True)
    values_n_flags = values_n_flags.rename(columns={0: "value", 1: "flag"})
    values_n_flags["value"] = values_n_flags["value"].str.replace(",", "")

    for line in df[new_columns]:
        for when in names:
            initial_content.append((",").join([line, when]))
    new_columns = (",").join([new_columns, "when"])
    new_df[new_columns] = initial_content

    columns = new_columns.split(",")
    new_df = new_df[new_columns].str.split(",", expand=True)
    new_df = new_df.rename(columns=dict(zip(list(new_df.columns), columns)))
    new_df = new_df.rename(columns={"GEO": "where"})
    new_df[["value", "flag"]] = values_n_flags

    new_df = pd.pivot_table(
        new_df,
        index=["where", "when"],
        columns=["AGE", "SEX", "INDIC_IL", "UNIT\\TIME"],
        values="value",
        aggfunc="first",
    )
    new_df.reset_index(level=["where", "when"], inplace=True)
    new_df.columns = new_df.columns.to_flat_index()
    new_df.columns = [
        ("income_" + column[0] + "_" + column[1] + "_" + column[2] + "_" + column[3]).lower()
        for column in new_df.columns
    ]
    new_df.rename(columns={"income_where___": "where", "income_when___": "when"}, inplace=True)
    new_df = new_df.replace(to_replace=":", value=np.nan)

    data = [pd.to_numeric(new_df[s], errors="ignore") for s in new_df.columns]
    new_df = pd.concat(data, axis=1, keys=[s.name for s in data])

    # Add when_type and where_type TODO: for example the euro area is now labeled as a country
    where_type = ["C"] * new_df.shape[0]
    when_type = ["year"] * new_df.shape[0]

    new_df["where_type"] = where_type
    new_df["when_type"] = when_type

    return new_df


def flatten_env(df):
    """
    Flatten a data frame so that each field contains a single value.
    """
    # Replace every underscore in DataFrame
    for column in df.columns:
        df[column] = df[column].str.replace("_", "-")
    new_df = pd.DataFrame()
    names = list(df.columns)
    new_columns = names.pop(0)

    initial_content = []
    values = df.values.tolist()
    values = [value[1:] for value in values]
    values = list(itertools.chain.from_iterable(values))
    values_n_flags = pd.DataFrame(values)[0].str.split(" ", expand=True)
    values_n_flags = values_n_flags.rename(columns={0: "value", 1: "flag"})
    values_n_flags["value"] = values_n_flags["value"].str.replace(",", "")

    for line in df[new_columns]:
        for when in names:
            initial_content.append((",").join([line, when]))
    new_columns = (",").join([new_columns, "when"])
    new_df[new_columns] = initial_content

    columns = new_columns.split(",")
    new_df = new_df[new_columns].str.split(",", expand=True)
    new_df = new_df.rename(columns=dict(zip(list(new_df.columns), columns)))
    new_df = new_df.rename(columns={"GEO": "where"})
    new_df[["value", "flag"]] = values_n_flags

    new_df = pd.pivot_table(
        new_df,
        index=["where", "when"],
        columns=["CEPAREMA", "ENV_ECON", "UNIT\\TIME"],
        values="value",
        aggfunc="first",
    )
    new_df.reset_index(level=["where", "when"], inplace=True)
    new_df.columns = new_df.columns.to_flat_index()
    new_df.columns = [("env_" + column[0] + "_" + column[1] + "_" + column[2]).lower() for column in new_df.columns]
    new_df.rename(columns={"env_where__": "where", "env_when__": "when"}, inplace=True)
    new_df = new_df.replace(to_replace=":", value=np.nan)

    data = [pd.to_numeric(new_df[s], errors="ignore") for s in new_df.columns]
    new_df = pd.concat(data, axis=1, keys=[s.name for s in data])

    # Add when_type and where_type TODO: for example the euro area is now labeled as a country
    where_type = ["C"] * new_df.shape[0]
    when_type = ["year"] * new_df.shape[0]

    new_df["where_type"] = where_type
    new_df["when_type"] = when_type

    return new_df


def run():

    cphi_df = pd.read_csv("../database/ei_cphi_m.tsv", sep="\t")
    health_out_of_pocket_df = pd.read_csv("../database/tepsr_sp310+ESTAT.tsv", sep="\t")
    income_df = pd.read_csv("../database/ilc_di03_1.tsv", sep="\t")
    env_df = pd.read_csv("../database/env_ac_epneec_1.tsv", sep="\t")

    # Flatten DataFrames
    cphi_df = flatten_cphi(cphi_df)
    health_out_of_pocket_df = flatten_health(health_out_of_pocket_df)
    income_df = flatten_income(income_df)
    env_df = flatten_env(env_df)

    # Merge DataFrames
    dfs = [cphi_df, income_df, health_out_of_pocket_df, env_df]
    df = pd.concat(dfs)

    # Clusters for countries
    clusteriser = CountryClusteriser()
    country_clusters_df = clusteriser.run()

    id_columns = ["when", "when_type", "where", "where_type"]
    base_columns = [column for column in df.columns if column not in id_columns]

    # Compare columns to EU average
    df = compare_to_eu(df, base_columns)

    # Compare columns to USA average
    df = compare_to_us(df, base_columns)

    # Compare to similar countries
    df = compare_to_similar(df, country_clusters_df, base_columns)

    # Rank value columns
    df = rank_df(df, base_columns)

    # Add outlierness to data
    outlierness_columns = [column for column in df.columns if column not in id_columns]
    df = add_outlierness_to_data(df, outlierness_columns, [])
    df.to_csv(os.path.join(os.path.dirname(__file__), "../data/eu_data.csv"), index=False)


if __name__ == "__main__":
    run()
