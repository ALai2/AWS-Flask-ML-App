# Import Pandas
import pandas as pd

# Import TfIdfVectorizer from scikit-learn
from sklearn.feature_extraction.text import TfidfVectorizer

# Import linear_kernel
from sklearn.metrics.pairwise import linear_kernel

import clean_info as ci 
import gender_pref_grps as gpg

# Define a TF-IDF Vectorizer Object. Remove all english stop words such as 'the', 'a'
tfidf = TfidfVectorizer(token_pattern=u'(?ui)\\b\\w*[a-z]+\\w*\\b', stop_words='english', use_idf = True)
# tfidf = TfidfVectorizer(token_pattern=u'(?ui)\\b\\w*[a-z]+\\w*\\b', stop_words='english', use_idf = False)

# groupby = 'Race'
groupby = None     

# data of people to be paired
csv = '2110Data.csv'

# round one variables
num = 2
rand_num = 4
do_random = False 

# round two variables
num2 = 2
rand_num2 = 3
do_random2 = True  

# important variable groups are features, replace, and weights

# feature groups - only for making manual editting easier
i_classes = ['Course1','Course2','Course3','Course4']
interests = ['Interest1','Interest2']

# features
features = ['Gender','Major','GradYear'] + i_classes + interests + ['StudyHabits','Hometown','CampusLocation','Race','Pref']
pair_features = i_classes # only needed if pair_groups is true
final_features = ['Name', 'Email', 'Phone'] + features

# replace
replace_space = i_classes + ['Major', 'Hometown','StudyHabits','CampusLocation']
replace_key = interests

# weights
c_weight = 16
i_weight = 8
weights = {'Name': 0, 'Gender': 0, 'Major': 5, 'GradYear': 7,
    'StudyHabits': 11, 'Hometown': 3, 'CampusLocation': 10, 'Race': 0, 'Pref': 0}
weights.update({ 'Course '+str((len(i_classes))+i): c_weight for i in range(1, len(i_classes)+1) })
weights.update({ 'Interest '+str((len(interests))+i): i_weight for i in range(1, len(interests)+1) })

preferences = {}
no_pref = "No preference"

# construct similarity matrix for group according to features and return pairings
def func_pairs(features, group, num, rand_num, do_random):
    # apply clean_df function to features
    m1 = group.copy()
    m1 = ci.clean_df(m1, features, replace_space, replace_key)
    if m1.empty:
        return []
    # BEGINNING ------------------------------------------------------------
    m1 = m1.assign(score = [''] * len(m1))
    for feature in features:
        if feature in weights:
            for i in range(weights[feature]):
                m1['score'] = m1['score'] + " " + m1[feature]
        else:
            m1['score'] = m1['score'] + " " + m1[feature]
        #to_add = m1[[feature]*weights[feature]].apply(lambda x: ' '.join(x), axis=1)
        #m1['score'] = m1['score'].str.cat(to_add, sep=" ", na_rep = "")
        
    print(m1)
    #Construct the required TF-IDF matrix by fitting and transforming the data
    tfidf_matrix = tfidf.fit_transform(m1['score'])

    # Compute the cosine similarity matrix
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    # END -----------------------------------------------------------------
    
    #Construct a reverse map of indices and employee names
    indices = pd.Series(group.index, index=group['index']).drop_duplicates()

    return get_pairs(group['index'].sample(frac=1), indices, cosine_sim, group, num, rand_num, do_random)

# minimize number of global variables
def convert_csv_to_matrix(metadata, num):
    final = metadata[final_features]
    final = final.reset_index()

    m0 = metadata[features]
    m0 = m0.reset_index()
    matches = []
    ones = []

    print_out = []
    groups_to_match = []
    if groupby is not None:
        courses = m0[groupby].unique() # list of all unique department names
        
        for course in courses:
            group = (m0[m0[groupby] == course]).reset_index().drop('level_0', axis=1)
            
            # keep track of groups with only one member
            if len(group) == 1:
                ones.append(group)
            else:
                matches = func_pairs(features, group, num, rand_num, do_random)
                if pair_features != []:
                    print_out += second_round(matches, m0)
                else:
                    print_out += [ ", ".join([ str(y) for y in x ]) for x in matches ] 
        
        if len(ones) != 0:
            if len(ones) == 1:
                print_out[0] += ", " + str(ones.pop(0)['index'].iloc[0])
            else:
                df = pd.DataFrame(columns=features + ['index'])
                
                for one in ones:
                    df = df.append(one, sort=False)
                df = df.reset_index().drop('level_0', axis=1)
                matches = func_pairs(features, df, num, rand_num, do_random)
                if pair_features != []:
                    print_out += second_round(matches, m0)
                else:
                    print_out += [ ", ".join([ str(y) for y in x ]) for x in matches ] 
    else:
        matches = func_pairs(features, m0, num, rand_num, do_random)
    
        if pair_features != []:
            print_out = second_round(matches, m0)
        else:
            print_out = [ ", ".join([ str(y) for y in x ]) for x in matches ] 
    
    # get the data of the people represented by indices to insert into csv
    total = []
    for group in print_out:
        index_list = group.split(", ")
        pairs = pd.DataFrame(columns=final_features + ['index'])
        for i in index_list:
            pairs = pairs.append(final[final['index'] == int(float(i))].iloc[0])
        total.append(pairs)
    # print this, output
    return total 

def second_round(matches, m0):
    # prepare first round pairings for second round pairings
    second_features = list.copy(pair_features)

    df = pd.DataFrame(columns=['unique_id'] + second_features)
    for pair in matches:
        lists = []
        for _ in range(len(second_features)):
            lists.append([])
        str_pair = [ str(x) for x in pair ]
        total_name = ", ".join(str_pair)

        data = [total_name]
        for i in pair:
            for feature in second_features:
                add = m0[feature][m0['index'] == i].iloc[0]
                if add == add:
                    lists[second_features.index(feature)].append(m0[feature][m0['index'] == i].iloc[0])
            
        for i in lists:
            if i != [] and not isinstance(i[0], str):
                for elem in range(len(i)):
                    i[elem] = str(i[elem])
            data.append(", ".join(i))

        pair_df = pd.DataFrame([data], columns=['unique_id'] + second_features)
        df = pd.concat([df, pair_df], sort=False)
 
    df = df.reset_index().drop('index', axis=1).reset_index()

    # complete second round pairings
    result = func_pairs(['unique_id'] + second_features, df, num2, rand_num2, do_random2)
    print_out = []
    for four in result:
        str_four = [ df[df['index'] == x].iloc[0][1] for x in four ]
        print_out.append(", ".join(str_four))
    return print_out

# Function that takes in movie title as input and outputs most similar movies
def get_recommendations(name, indices, cosine_sim, list_to_remove, m0, num):
    # Get the index of the employee that matches the name
    idx = indices[name]

    # Get the pairwsie similarity scores of all employees with that employee
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = [(key, val) for (key, val) in sim_scores if key not in list_to_remove]
    
    # general preferences, not just GenderPref
    
    ratio_inc = 1
    for pref in preferences:
        # Increase similarity scores for people who idx prefers
        idx_pref = m0[m0.index==idx][pref].iloc[0]
        if (idx_pref == idx_pref):
            pref_df = m0.query(str(preferences[pref]) + ' == "' + str(idx_pref) + '"')[["index"]]
            pref_indices = pref_df.index.values.tolist()
            sim_scores = [(key, val) if key not in pref_indices else (key, val + ratio_inc) for (key, val) in sim_scores]
        
        # Increase similarity scores for people who prefer idx
        idx_gender = m0[m0.index==idx][preferences[pref]].iloc[0]
        if (idx_pref == idx_pref):
            pref_df = m0.query(str(pref) + ' == "' + str(idx_gender) + '"')[["index"]]
            pref_indices = pref_df.index.values.tolist()
            sim_scores = [(key, val) if key not in pref_indices else (key, val + ratio_inc) for (key, val) in sim_scores]

    # Sort the employees based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    num_indices = [key for (key, val) in sim_scores[0:num+1]]
    
    num_sims = [val for (key, val) in sim_scores[0:num+1]]

    # Return the top group_num most similar people not already paired
    result = m0.iloc[num_indices]
    result = result.assign(Similarity = num_sims) # still need this?
    return result 

import random 
# choose partners from list of top similar people from get_recommendations
def get_random(idx, m0, mylist, num, do_random): # num = number of people per group
    if (len(mylist) > num):
        inds = list(mylist.index)
        result = pd.DataFrame(columns=features)
        cur_size = 0
        already_selected = []

        if do_random:
            rand_inds = random.sample(inds, num-1)
            for i in rand_inds:
                if i not in already_selected:
                    already_selected.append(i)
                    result = pd.concat([result, mylist[mylist.index == i]], sort=False)
                    cur_size = cur_size + 1
                    if cur_size == num-1:
                        return result
        else:
            return mylist.head(num-1)
    else:
        result = mylist
    return result

# loop through list of people and pair people not already paired
def get_pairs(emplist, indices, cosine_sim, m0, num, rand_num, do_random):
    pairs = []
    list_to_remove = []
    
    for e in emplist:
        if indices[e] not in list_to_remove:
            list_to_remove.append(indices[e])
            partner = list(get_random(indices[e], m0, get_recommendations(e, indices, cosine_sim, list_to_remove, m0, num), num, do_random)['index'])
            name0 = e
            pair = [name0]
            
            for p in partner:
                pair.append(p)
                list_to_remove.append(indices[p])

            pairs.append(pair)
            
            list_to_remove.sort(reverse=True)
    return pairs

def run_file(csv, lists, we, pf, options):
    global features
    global pair_features
    global final_features
    global replace_space
    global replace_key
    global weights
    global preferences
    global groupby

    global num
    global rand_num
    global do_random

    global num2
    global rand_num2
    global do_random2 

    features = lists[0]
    pair_features = lists[1]
    replace_key = lists[2]
    replace_space = lists[3]
    final_features = lists[4]
    weights = we
    preferences = pf

    num = options[0]
    num2 = options[1]
    rand_num = options[2]
    do_random = True
    do_random2 = True
    if rand_num == 0 or rand_num <= num:
        do_random = False
    rand_num2 = options[3]
    if rand_num2 == 0 or rand_num2 <= num2:
        do_random2 = False
    
    groupby = None
    if options[4] != None:
        groupby = options[4]

    old_df = pd.read_csv(csv)
    new_groups = gpg.split_into_groups(old_df)  #

    new_df_lst = []
    #new_df_lst.extend(convert_csv_to_matrix(old_df, num))  #
    
    for i in range(len(new_groups)):   #
        use_num = num                  #
        if i == 1:                     #
            pair_features = lists[0]   #
            use_num = 2                #
            num2 = int(num / 2)        #
        else:                          #
            pair_features = []         #
        new_df_lst.extend(convert_csv_to_matrix(new_groups[i], use_num))   #
    
    data = [['-'] * (len(final_features)+1)]
    data2 = [['+'] * (len(final_features)+1)]

    # for spacing
    extra = pd.DataFrame(data, columns=final_features + ['index'])
    extra2 = pd.DataFrame(data2, columns=final_features + ['index'])
    #pairs = pd.concat([pairs, extra, extra2], sort=False)
    fours = []
    others = []
    for group in new_df_lst:
        if len(group) == 4:
            fours.append(group)
            fours.append(extra)
            fours.append(extra2)
        else:
            others.append(group)
            others.append(extra)
            others.append(extra2)
    
    fours_df = pd.concat(fours)
    others_df = pd.concat(others)
    total_df = pd.concat([fours_df, others_df], sort=False)
    total_df.to_csv('testing.csv', index=False)