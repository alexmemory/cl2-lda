import pandas as pd

def split_reactions_file(path_to_csv):
    """Clean up and split the reactions file into separate tables
    This will return a dictionary containing pandas tables:
    - The reactions
    - The questionnaire responses
    - The demographic portion of the questionnaire
    - The political portion of the questionnaire
    """
    a = pd.read_csv(path_to_csv)
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
    a['Time'] = pd.to_datetime(a['Time'])
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

def link_reactions_to_transcript(path_to_reactions_file, path_to_transcript_file, truncate_after='2:33'):
    """Return a table with reactions data next to transcript entries
    This will return a table with an entry for each reaction and columns
    from the reaction data, plus the most recent statement from the transcript.
    It removes reactions before the debate stated (about 1/2 hour) and after
    the debate ended (about 1/2 hour).
    """

    parts = split_reactions_file(path_to_reactions_file)
    r = parts['reactions']

    r['start'] = r.Time.apply(lambda t: pd.datetime.time(t)) # A col to merge on

    c = pd.read_csv(path_to_transcript_file)
    c['start'] = pd.to_datetime(c["Sync'd start"]).apply(lambda t: pd.datetime.time(t))
    c['statement'] = range(len(c))

    m = c.append(r) # merge on 'state' col
    m = m.sort(columns='start') # sort on 'state'
    m = m.fillna(method='ffill') # give last transcript info to subsequent reactions

    m = m.dropna() # remove reactions without transcript info

    m = m[m.start < pd.datetime.time(pd.to_datetime(truncate_after))] # remove reactions after the debate

    m['turn'] = (m.Speaker.shift(1) != m.Speaker).astype(int).cumsum() # identify turns

    return m
