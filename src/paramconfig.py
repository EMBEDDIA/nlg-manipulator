"""
Configuration file containing 'importance' constants for facts
"""

#regarding who_type
party_score = 1.0
candidate_score = 0.5
candidate_memb_score = 0.6

#regarding location_type
municipality_score = 1.0
country_score = 0.7
voting_district_score = 0.5
polling_station_score = 0.5

#regarding what_type
base_seats = 3
base_perc_votes = 2
base_total_votes = 1
base_election_result = 1.5
comparison_empty = 4
comparison_change = 2
comparison_prev_election = 1
stats_rank = 2
stats_empty = 1

#regarding outlyingness value
value_out_score = 0.01 # if what_value = Q2
out_zero_score = 1 # if q3 and q1 are equal

#giving the percentage_votes_rank and the percentage_votes_change_rank facts a very low importance
low_importance = 0.0001