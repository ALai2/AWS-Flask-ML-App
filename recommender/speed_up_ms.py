import pandas as pd

import clean_info as ci 
import model_selection as ms # use model selection for predictions
import random 

csv = 'Prof Clarkson Test Data - Sheet1 (1).csv'
primary = 'Name'

use_index = True  

training_features = ['Name','Gender','Major','Grad Year','Classes 1','Interests','Study Habits','Hometown','Campus Location','Race','Preferences']
second_features = ['Name','Classes 2']

# add combine variables?
def speed_up_pairings(features, m0, num, rand_num, do_random, i_classes, model_num, combine):

    m1 = m0.copy()
    m1 = ci.clean_df(m1, features, primary, i_classes)
    
    if use_index:
        names = list(m1['index'])
    else:
        names = list(m1['Name'])

    data = [['-'] * (len(features)+1)]
    extra = pd.DataFrame(data, columns=features + ['index'])

    # pairs = pd.DataFrame(columns=features + ['index'])
    pairs = []
    already_paired = []
    not_paired = names 
    for n in names:
        if n not in already_paired:
            pair = []
            not_paired.remove(n)
            already_paired.append(n)
                
            if use_index:
                # pairs = pairs.append(m0[m0['index'] == n].iloc[0])
                pair.append(n)
            else:
                n_index = m1['index'][m1['Name'] == n].iloc[0]
                # pairs = pairs.append(m0[m0['index'] == n_index].iloc[0])
                pair.append(n_index)

            data = [ [str(n) + "; " + str(x)] if use_index else [n + "; " + x] for x in not_paired ]
            df = pd.DataFrame(data, columns=['group'])

            df_soup = ms.load_prediction(df, m1, model_num, combine)
            if model_num == 1:
                t_features = training_features
            elif model_num == 2:
                t_features = second_features
            X_test = df_soup[[x for x in t_features if x != primary]]
            predictions = ms.make_prediction(df_soup, X_test, model_num) # already sorted

            group_sims = []
            if do_random: group_num = rand_num 
            else: group_num = num + 1
            for p in predictions.iterrows():
                if (len(group_sims) == group_num): break
                n, x = (p[1]['Name']).split("; ")
                group_sims.append(x)
                
            if (len(group_sims) > num):
                if do_random:
                    result = random.sample(group_sims, num-1)
                else:
                    result = group_sims[:num-1]
            else:
                result = group_sims
                
            if use_index:
                matches = [ int(x) for x in result ]
                not_paired = [ x for x in not_paired if x not in matches ]
                already_paired += matches
            else: 
                already_paired += result
                not_paired = [ x for x in not_paired if x not in result ]
                matches = [ m1['index'][m1['Name'] == m].iloc[0] for m in result ]

            for m in matches:
                # pairs = pairs.append(m0[m0['index'] == m].iloc[0])
                pair.append(m)
                
            # pairs = pd.concat([pairs, extra], sort=False)
            pairs.append(pair)

    return pairs  