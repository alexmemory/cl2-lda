# Generates evaluation results for the NGrams baseline
# 
# To run: python baseline_ngrams.py <path to reactions CSV file> <path to coded transcript CSV file> <unigram/bigram>
#

import pandas as pd
import reactions
import nltk
import random
import numpy as np
from numpy import *
import sys
from nltk.corpus import stopwords

if len(sys.argv) < 2:
    print "usage: <path to reactions CSV file> <path to coded transcript CSV file> <unigram/bigram>"
    sys.exit()

idk,rfile,tfile,ngram_type = sys.argv

# A table of reactions associated with transcript statements 
print '{:_^80}'.format('linking reactions to transcript'.upper())
r = reactions.link_reactions_to_transcript(rfile,tfile)

r2 = r.copy()
del r2["Time"]
del r2["Speaker"]

# The political preferences portion of the questionnaire
p = reactions.split_reactions_file(rfile)['quest_political']

p2 = p[['UserID','party_1','political_views_2','candidate_choice_3','confidence_in_choice_4','likely_to_vote_5','candidate_preferred_29']]

# Simplify party membership into R/D/oth
p2['party'] = p2.party_1.apply(lambda a: {'closest to democratic party':'democrat', 
                                          'lean democrat':'democrat',
                                          'lean republican':'republican',
                                          'closest to republican party':'republican'}.get(a,'other'))
p2['candidate'] = p2.candidate_choice_3

# Merge political questionnaire with reactions
print '{:_^80}'.format('merging questionnaire info with transcript'.upper())
r3 = r2.merge(p2[['UserID','party','candidate']])

# Limit to reactions to the speaker of the ***current turn***.
r4 = r3[r3.Reaction_who == r3.Speaker_name]

# Group by turn

# Statements
print '{:_^80}'.format('grouping by statement'.upper())
st = r4.groupby(['statement']).first()[['Speaker_name','Transcript','turn',"Sync'd start","Sync'd end"]]

# Turns
print '{:_^80}'.format('grouping by turn'.upper())
t = pd.DataFrame({'speaker':st.groupby('turn').first().Speaker_name, 
                  'start':st.groupby('turn').first()["Sync'd start"],
                  'end':st.groupby('turn').last()["Sync'd end"],
                  #'reactions':r4.groupby('turn').count().Speaker_name, 
                  'reactions_oba':r4[(r4.candidate=='obama')].groupby('turn').count().turn,
                  'reactions_rom':r4[(r4.candidate=='romney')].groupby('turn').count().turn,
                  'statements':st.groupby('turn').count().turn, 
                  'text':st.groupby('turn').apply(lambda x: ''.join(x.Transcript)),
                  'agree':r4[r4.Reaction_what=='Agree'].groupby('turn').count().turn,
                  'agree_dem':r4[(r4.party=='democrat') & (r4.Reaction_what=='Agree')].groupby('turn').count().turn,
                  'agree_rep':r4[(r4.party=='republican') & (r4.Reaction_what=='Agree')].groupby('turn').count().turn,
                  'agree_oba':r4[(r4.candidate=='obama') & (r4.Reaction_what=='Agree')].groupby('turn').count().turn,
                  'agree_rom':r4[(r4.candidate=='romney') & (r4.Reaction_what=='Agree')].groupby('turn').count().turn,
                  'disagree':r4[r4.Reaction_what=='Disagree'].groupby('turn').count().turn,
                  'disagree_dem':r4[(r4.party=='democrat') & (r4.Reaction_what=='Disagree')].groupby('turn').count().turn,
                  'disagree_rep':r4[(r4.party=='republican') & (r4.Reaction_what=='Disagree')].groupby('turn').count().turn,
                  'disagree_oba':r4[(r4.candidate=='obama') & (r4.Reaction_what=='Disagree')].groupby('turn').count().turn,
                  'disagree_rom':r4[(r4.candidate=='romney') & (r4.Reaction_what=='Disagree')].groupby('turn').count().turn,
                  'dodge_oba':r4[(r4.candidate=='obama') & (r4.Reaction_what=='Dodge')].groupby('turn').count().turn,
                  'dodge_rom':r4[(r4.candidate=='romney') & (r4.Reaction_what=='Dodge')].groupby('turn').count().turn,
                  'dodge':r4[r4.Reaction_what=='Dodge'].groupby('turn').count().turn,
                  'spin_oba':r4[(r4.candidate=='obama') & (r4.Reaction_what=='Spin')].groupby('turn').count().turn,
                  'spin_rom':r4[(r4.candidate=='romney') & (r4.Reaction_what=='Spin')].groupby('turn').count().turn,
                  'spin':r4[r4.Reaction_what=='Spin'].groupby('turn').count().turn,
                  })
tmpstart = pd.to_datetime(t.start)
tmpend = pd.to_datetime(t.end)
t['dur'] = (tmpend - tmpstart)
t.duration = 1.0 * t.dur / 1000000000.0
t['words'] = t.text.apply(lambda txt: [tok.lower() for tok in nltk.tokenize.word_tokenize(txt) if tok.isalpha()])
t['word_count'] = t.words.apply(lambda words: len(words))
#t['r_per_st'] = 1.0 * t.reactions / t.statements
#t['r_per_w'] = 1.0 * t.reactions / t.word_count
#t['r_per_sec'] = 1.0 * t.reactions / t.dur
t['rps_oba'] = 1.0 * t.reactions_oba / t.dur
t['rps_rom'] = 1.0 * t.reactions_rom / t.dur
#t['sd_per_sec'] = 1.0 * (t.spin + t.dodge) / t.dur
t['sdps_oba'] = 1.0 * (t.spin_oba + t.dodge_oba) / t.dur
t['sdps_rom'] = 1.0 * (t.spin_rom + t.dodge_rom) / t.dur
t['a_to_d_dems'] = t.agree_dem / t.disagree_dem
t['a_to_d_reps'] = t.agree_rep / t.disagree_rep
t['a_to_d_oba'] = t.agree_oba / t.disagree_oba
t['a_to_d_rom'] = t.agree_rom / t.disagree_rom
del t['agree']
#del t['agree_dem']
#del t['agree_rep']
del t['disagree']
#del t['disagree_dem']
#del t['disagree_rep']
del t['dodge']
del t['spin']
#del t['r_per_st']
#del t['r_per_w']
del t['start']
del t['end']
del t['dur']

# NGram Features
print '{:_^80}'.format('generating ngram features'.upper())
all_words = [w for word_list in t.words for w in word_list]
all_bigrams = nltk.bigrams(all_words)
ranked_unigrams = nltk.FreqDist(all_words).keys()
ranked_bigrams = nltk.FreqDist(all_bigrams).keys()
#MAX_FEATURES = 200 # avoid overfitting
MAX_FEATURES = 700 # avoid overfitting
t['unigrams'] = t.words.apply(lambda words: {w:True for w in words if w in ranked_unigrams[:MAX_FEATURES] and not w in stopwords.words('english')})
t['bigrams'] = t.words.apply(lambda words: {"%s_%s"%(w1,w2):True for w1,w2 in nltk.bigrams(words) if 
                                            (w1,w2 in ranked_bigrams[:MAX_FEATURES]) and
                                            (not w1 in stopwords.words('english')) and
                                            (not w2 in stopwords.words('english'))
                                            })

# We get rid of the really short turns.
MIN_WORDS = 30 
t2 = t[t.word_count >= MIN_WORDS]


# Crossvalidation code
def cv(df, num_folds = 10, classifier=nltk.NaiveBayesClassifier, maxent_params=None, print_features=False):
    df = df.copy()
    df = df.reindex(np.random.permutation(df.index))
    fold_size = len(df)/num_folds
    fold_starts = range(0, len(df)+fold_size, fold_size)
    folds = zip(fold_starts,fold_starts[1:])
    accs = []
    for (first,last) in folds:
        test_rows = df.index[first:last]
        tst = df.ix[test_rows]
        trn = df.drop(test_rows)
        if maxent_params == None:
            cl = classifier.train(zip(trn.features, trn.label))
        else:
            cl = classifier.train(zip(trn.features, trn.label), 
                                  algorithm=maxent_params['algorithm'], 
                                  max_iter=maxent_params['max_iter'],
                                  trace=maxent_params['trace'])
        accs.append(nltk.classify.accuracy(cl, zip(tst.features, tst.label)))
    return {'mean':mean(accs),'stdev':std(accs)}

# N-Gram Type
if (ngram_type == 'bigram'):
    t2['features'] = t2.bigrams
elif(ngram_type == 'unigram'):
    t2['features'] = t2.unigrams
else:
    print 'unkown ngram type:',ngram_type
    sys.exit()

# Task 1: Reactions per second

print '{:_^80}'.format('task 1 obama supporters'.upper())
e1 = t2.copy()
e1['label'] = e1.rps_oba >= e1.rps_oba.quantile(.5)
print 'DT', cv(e1, classifier=nltk.classify.DecisionTreeClassifier)
print 'ME', cv(e1, classifier=nltk.classify.MaxentClassifier, 
               maxent_params={'algorithm':nltk.classify.MaxentClassifier.ALGORITHMS[0], 
                              'max_iter':25,
                              'trace':0})
print 'NB', cv(e1, classifier=nltk.NaiveBayesClassifier)

print '{:_^80}'.format('task 1 romney supporters'.upper())
e1 = t2.copy()
e1['label'] = e1.rps_rom >= e1.rps_rom.quantile(.5)
print 'DT', cv(e1, classifier=nltk.classify.DecisionTreeClassifier)
print 'ME', cv(e1, classifier=nltk.classify.MaxentClassifier, 
               maxent_params={'algorithm':nltk.classify.MaxentClassifier.ALGORITHMS[0], 
                              'max_iter':25,
                              'trace':0})
print 'NB', cv(e1, classifier=nltk.NaiveBayesClassifier)

#e1['label'] = e1.rps_rom >= e1.rps_rom.quantile(.5)
#train_rows = random.sample(e1.index, len(e1)*9/10)
#trn = e1.ix[train_rows]
#tst = e1.drop(train_rows)
#cl = nltk.NaiveBayesClassifier.train(zip(trn.features, trn.label))
#nltk.classify.accuracy(cl, zip(tst.features, tst.label))
#cl.show_most_informative_features(25)

# Task 2a: Majority agrees with speaker

print '{:_^80}'.format('task 2 obama supporters'.upper())
e2ad = t2.copy()
e2ad['label'] = e2ad.agree_oba >= e2ad.disagree_oba
print 'DT', cv(e2ad, classifier=nltk.classify.DecisionTreeClassifier)
print 'ME', cv(e2ad, classifier=nltk.classify.MaxentClassifier, 
               maxent_params={'algorithm':nltk.classify.MaxentClassifier.ALGORITHMS[0], 
                              'max_iter':25,
                              'trace':0})
print 'NB', cv(e2ad, classifier=nltk.NaiveBayesClassifier)

#e2ad['label'] = e2ad.agree_oba >= e2ad.disagree_oba
#train_rows = random.sample(e2ad.index, len(e2ad)*9/10)
#trn = e2ad.ix[train_rows]
#tst = e2ad.drop(train_rows)
#cl = nltk.NaiveBayesClassifier.train(zip(trn.features, trn.label))
#nltk.classify.accuracy(cl, zip(tst.features, tst.label))
#cl.show_most_informative_features(25)


print '{:_^80}'.format('task 2 romney supporters'.upper())
e2ar = t2.copy()
e2ar['label'] = e2ar.agree_rom >= e2ar.disagree_rom
print 'DT', cv(e2ar, classifier=nltk.classify.DecisionTreeClassifier)
print 'ME', cv(e2ar, classifier=nltk.classify.MaxentClassifier, 
               maxent_params={'algorithm':nltk.classify.MaxentClassifier.ALGORITHMS[0], 
                              'max_iter':25,
                              'trace':0})
print 'NB', cv(e2ar, classifier=nltk.NaiveBayesClassifier)

#e2ar['label'] = e2ar.agree_rom >= e2ar.disagree_rom
#train_rows = random.sample(e2ar.index, len(e2ar)*9/10)
#trn = e2ar.ix[train_rows]
#tst = e2ar.drop(train_rows)
#cl = nltk.NaiveBayesClassifier.train(zip(trn.features, trn.label))
#nltk.classify.accuracy(cl, zip(tst.features, tst.label))
#cl.show_most_informative_features(25)

# Task 3: Spins+dodges per second above median

print '{:_^80}'.format('task 3 obama supporters'.upper())
e3 = t2.copy()
e3['label'] = e3.sdps_oba >= e3.sdps_oba.quantile(.5)
print 'DT', cv(e3, classifier=nltk.classify.DecisionTreeClassifier)
print 'ME', cv(e3, classifier=nltk.classify.MaxentClassifier, 
               maxent_params={'algorithm':nltk.classify.MaxentClassifier.ALGORITHMS[0], 
                              'max_iter':25,
                              'trace':0})
print 'NB', cv(e3, classifier=nltk.NaiveBayesClassifier)

print '{:_^80}'.format('task 3 romney supporters'.upper())
e3 = t2.copy()
e3['label'] = e3.sdps_rom >= e3.sdps_rom.quantile(.5)
print 'DT', cv(e3, classifier=nltk.classify.DecisionTreeClassifier)
print 'ME', cv(e3, classifier=nltk.classify.MaxentClassifier, 
               maxent_params={'algorithm':nltk.classify.MaxentClassifier.ALGORITHMS[0], 
                              'max_iter':25,
                              'trace':0})
print 'NB', cv(e3, classifier=nltk.NaiveBayesClassifier)
