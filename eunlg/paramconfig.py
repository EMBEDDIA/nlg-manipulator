"""
Configuration file containing 'importance' constants for crime facts
"""

# Regarding the crime what_type
# The parameters are based on the severity of the punishment, given under the  Criminal Code Finland.
# Since they are different crimes under each category, we consider the most severe of the crime_types in that category
# and base the score on that. There are 5 severety categories with life_offences having the highest punishment
# (i.e., life imprisonment), gets a importance of 5. Next is crimes sentenced a max of 10 years which get a score of 4,
# then others that have 4 years, 2 years, and 0 years that get a score of 3, 2, and 1 respectively.
# Source of the sentences are available here: https://www.finlex.fi/en/laki/kaannokset/1889/en18890039.pdf

# dictionary of parameters

value_type_re = (
    r"([0-9_a-z\-.]+?)(_normalized)?(?:(_mk_score|_mk_trend)|(_percentage)?(_change)?(?:(?:_grouped_by)"
    r"(_time_place|_time|_place_year))?((?:_decrease|_increase)?_rank(?:_reverse)?)?)"
)

category_scores = {
    "life": 10,
    "health": 10,
    "sexual": 10,
    "narcotics": 7,
    "property": 7,
    "authority": 5,
    "alcohol": 3,
    "traffic": 2,
    "other": 0.001,
    "investigations": 0.001,
}

rank_reverse_weight = 1
rank_weight = 2

comp_weight = 200

comparison_change = 3
# I am making the assumption that the comparison_change is more important in crime data than the comparison_empty,
# unlike the election data?
comparison_empty = 2

stats_rank = 2
stats_empty = 1

# regarding outlyingness value
value_out_score = 0.01  # if what_value = Q2
out_zero_score = 1  # if q3 and q1 are equal
