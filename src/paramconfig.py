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

base_property_offences_total = 3
base_life_offences_total = 5
base_health_offences_total = 4
base_sexual_crimes_total = 4
base_authority_related_offences_total = 3
base_traffic_offences_total = 2
base_narcotic_offences_total = 4
base_alcohol_offences_total = 3
base_investigations_total = 1
base_other_offences_total = 3

comparison_change = 4
# I am making the assumption that the comparison_change is more important in crime data than the comparison_empty,
# unlike the election data?
comparison_empty = 2

stats_rank = 2
stats_empty = 1

#regarding outlyingness value
value_out_score = 0.01 # if what_value = Q2
out_zero_score = 1 # if q3 and q1 are equal

#giving the percentage_votes_rank and the percentage_votes_change_rank facts a very low importance
low_importance = 0.0001 # Is this still need for crime data?