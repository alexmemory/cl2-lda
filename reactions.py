import pandas

def split_reactions_file(path_to_csv):
    """Clean up and split the reactions file into separate tables
    This will return a dictionary containing pandas tables:
    - The reactions
    - The questionnaire responses
    - The demographic portion of the questionnaire
    - The political portion of the questionnaire
    """
    a = pandas.read_csv(path_to_csv)
    a.columns = [c.strip() for c in """
    UserID
    Reaction
    Time
    how_watching_25
    economy_priority_10
    health_care_party_12
    foreign_policy_party_13
    abortion_party_14
    economy_party_15
    health_care_priority_7
    foreign_policy_priority_8
    abortion_priority_9
    interested_23
    news_sources_24
    gender_16
    age_17
    family_income_18
    race_19
    religion_20
    christian_21
    state_22
    tv_channel_26
    economy_candidate_27
    foreign_policy_candidate_28
    candidate_preferred_29
    candidate_choice_3
    confidence_in_choice_4
    likely_to_vote_5
    political_views_2
    ready
    immigration_priority_6
    immigration_party_11
    party_1
    next
    """.split('\n') if not c.strip()=='']

    a = a.reindex(columns=[c.strip() for c in """
    UserID
    Time
    Reaction
    party_1
    political_views_2
    candidate_choice_3
    confidence_in_choice_4
    likely_to_vote_5
    immigration_priority_6
    health_care_priority_7
    foreign_policy_priority_8
    abortion_priority_9
    economy_priority_10
    immigration_party_11
    health_care_party_12
    foreign_policy_party_13
    abortion_party_14
    economy_party_15
    gender_16
    age_17
    family_income_18
    race_19
    religion_20
    christian_21
    state_22
    interested_23
    news_sources_24
    how_watching_25
    tv_channel_26
    economy_candidate_27
    foreign_policy_candidate_28
    candidate_preferred_29
    ready
    next
    """.split('\n') if not c.strip()==''])

    a['Reaction_who'] = a.Reaction.str.split(':').str.get(0)
    a['Reaction_what'] = a.Reaction.str.split(':').str.get(1)
    a['Time'] = pandas.to_datetime(a['Time'])
    r = a[['UserID','Time','Reaction_who','Reaction_what']]

    q = a[[c.strip() for c in """
    UserID
    party_1
    political_views_2
    candidate_choice_3
    confidence_in_choice_4
    likely_to_vote_5
    immigration_priority_6
    health_care_priority_7
    foreign_policy_priority_8
    abortion_priority_9
    economy_priority_10
    immigration_party_11
    health_care_party_12
    foreign_policy_party_13
    abortion_party_14
    economy_party_15
    gender_16
    age_17
    family_income_18
    race_19
    religion_20
    christian_21
    state_22
    interested_23
    news_sources_24
    how_watching_25
    tv_channel_26
    economy_candidate_27
    foreign_policy_candidate_28
    candidate_preferred_29
    ready
    next
    """.split('\n') if not c.strip()=='']]

    q = q.drop_duplicates()

    d = q[[c.strip() for c in """
    gender_16
    age_17
    family_income_18
    race_19
    religion_20
    christian_21
    state_22
    """.split('\n') if not c.strip()=='']]

    p = q[[c.strip() for c in """
    party_1
    political_views_2
    candidate_choice_3
    confidence_in_choice_4
    likely_to_vote_5
    immigration_priority_6
    health_care_priority_7
    foreign_policy_priority_8
    abortion_priority_9
    economy_priority_10
    immigration_party_11
    health_care_party_12
    foreign_policy_party_13
    abortion_party_14
    economy_party_15
    interested_23
    news_sources_24
    economy_candidate_27
    foreign_policy_candidate_28
    candidate_preferred_29
    """.split('\n') if not c.strip()=='']]

    return {'reactions':r, 'questionnaire':q, 'quest_demographic':d, 'quest_political':p}
