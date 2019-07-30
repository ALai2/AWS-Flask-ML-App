# Import Pandas
import pandas as pd

# Import TfIdfVectorizer from scikit-learn
from sklearn.feature_extraction.text import TfidfVectorizer

# Import linear_kernel
from sklearn.metrics.pairwise import linear_kernel

import json # for testing
import clean_info as ci 
import model_selection as ms 

# Define a TF-IDF Vectorizer Object. Remove all english stop words such as 'the', 'a'
tfidf = TfidfVectorizer(token_pattern=u'(?ui)\\b\\w*[a-z]+\\w*\\b', stop_words='english', use_idf = True)
# tfidf = TfidfVectorizer(token_pattern=u'(?ui)\\b\\w*[a-z]+\\w*\\b', stop_words='english', use_idf = False)

primary = 'Name'
# groupby = 'Race'
groupby = None
use_model = False 
replace_list = ['Interest 1','Interest 2']

# data of people to be paired
csv = 'Prof Clarkson Test Data - Sheet1 (1).csv'

# round one variables
num = 2
rand_num = 4
do_random = False 

# round two variables
pair_groups = True  # use_model = True does not work with pair_groups = True 
num2 = 2
rand_num2 = 3
do_random2 = False 

# features
# features = ['Name', 'Major','Class 1','Class 2','Class 3','Class 4','Interest 1','Interest 2','Interest 3','Hometown','Hometype']
# weights = {'Name': 0, 'Major': 30, 'Class 1': 20, 'Class 2': 20, 'Class 3': 20, 'Class 4': 20, 'Interest 1': 12, 'Interest 2': 12, 'Interest 3': 12, 'Hometown': 18, 'Hometype': 0}
i_classes = ['Class 1','Class 2','Class 3','Class 4']
features = ['Name','Gender','Major','Grad Year'] + i_classes + ['Interest 1','Interest 2','Study Habits','Hometown','Campus Location','Race','Preferences']
c_weight = 16
i_weight = 8
weights = {'Name': 0, 'Gender': 0, 'Major': 5, 'Grad Year': 7, 
    'Interest 1': i_weight, 'Interest 2': i_weight, 
    'Study Habits': 11, 'Hometown': 3, 'Campus Location': 10, 'Race': 0, 'Preferences': 0}

if pair_groups:
    for n in range(0, num):
        weights.update({ 'Class '+str((n*len(i_classes))+i): c_weight for i in range(1, len(i_classes)+1) })
else:
    weights.update({ 'Class '+str((len(i_classes))+i): c_weight for i in range(1, len(i_classes)+1) })

# construct similarity matrix for group according to features and return pairings
def func_pairs(features, group, num, rand_num, do_random):
    # apply clean_df function to features
    m1 = group.copy()
    m1 = ci.clean_df(m1, features, primary)
        
    if use_model: # how to make this work?
        cosine_sim = ms.construct_similarity(m1)
    else:
        # BEGINNING ------------------------------------------------------------
        m1 = m1.assign(score = [''] * len(m1))
        for feature in features:
            if feature in weights:
                for i in range(weights[feature]):
                    m1['score'] = m1['score'] + " " + m1[feature]
            else:
                m1['score'] = m1['score'] + " " + m1[feature]
        
        #Construct the required TF-IDF matrix by fitting and transforming the data
        tfidf_matrix = tfidf.fit_transform(m1['score'])

        # Compute the cosine similarity matrix
        cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
        # END -----------------------------------------------------------------
    
    #Construct a reverse map of indices and employee names
    indices = pd.Series(group.index, index=group['index']).drop_duplicates()

    return get_pairs(group['index'].sample(frac=1), indices, cosine_sim, group, num, rand_num, do_random)

# minimize number of global variables
def convert_csv_to_matrix(csv, num):
    # Load data from csv
    metadata = pd.read_csv(csv)
    m0 = metadata[features]

    for feature in replace_list:
        m0[feature] = m0[feature].apply(ci.key_replace)

    m0 = m0.reset_index()
    group_dict = {}
    matches = []
    ones = []

    if groupby is not None:
        courses = m0[groupby].unique() # list of all unique department names
        
        for course in courses:
            group = (m0[m0[groupby] == course]).reset_index().drop('level_0', axis=1)
            
            # keep track of groups with only one member
            if len(group) == 1:
                ones.append(group)
            else:
                matches += func_pairs(features, group, num, rand_num, do_random)
        
        if len(ones) != 0:
            if len(ones) == 1:
                for match in matches:
                    if len(ones) == 0: break
                    else:
                        while len(match) < num:
                            if len(ones) != 0:
                                match.append(ones.pop(0)[primary])
                            else: break
                if len(ones) > 0:
                    matches[0].append(ones.pop(0))
            else:
                df = pd.DataFrame(columns=features + ['index'])
                
                for one in ones:
                    df = df.append(one, sort=False)
                df = df.reset_index().drop('level_0', axis=1)
                matches += func_pairs(features, df, num, rand_num, do_random)
    else:
        matches = func_pairs(features, m0, num, rand_num, do_random)
    
    if pair_groups:
        # prepare first round pairings for second round pairings
        pair_features = ['Name']
        for n in range(0, num):
            pair_features += [ 'Class '+str((n*len(i_classes))+i) for i in range(1, len(i_classes)+1)]
        
        df = pd.DataFrame(columns=pair_features)
        for pair in matches:
            str_pair = [ str(x) for x in pair ]
            total_name = ", ".join(str_pair)

            data = [total_name]
            for i in pair:
                for feature in i_classes:
                    data.append(m0[feature][m0['index'] == i].iloc[0])
            
            # take care of missing data
            while(len(data) < len(pair_features)):
                data.append("")

            pair_df = pd.DataFrame([data], columns=pair_features)
            df = pd.concat([df, pair_df], sort=False)
        df = df.reset_index().drop('index', axis=1).reset_index()

        # complete second round pairings
        result = func_pairs(pair_features, df, num2, rand_num2, do_random2)

        print_out = []
        for four in result:
            str_four = [ df[primary][df['index'] == x].iloc[0] for x in four ]
            print_out.append(", ".join(str_four))
    else:
        print_out = [ ", ".join([ str(y) for y in x ]) for x in matches ] 
    
    # get the data of the people represented by indices to insert into csv
    pairs = pd.DataFrame(columns=features + ['index'])
    for group in print_out:
        index_list = group.split(", ")
        for i in index_list:
            pairs = pairs.append(m0[m0['index'] == int(float(i))].iloc[0])
        data = [['-'] * (len(features)+1)]
        data2 = [['+'] * (len(features)+1)]

        # for spacing
        extra = pd.DataFrame(data, columns=features + ['index'])
        extra2 = pd.DataFrame(data2, columns=features + ['index'])
        pairs = pd.concat([pairs, extra, extra2], sort=False)

    # print this, output
    return pairs 

# Function that takes in movie title as input and outputs most similar movies
def get_recommendations(name, indices, cosine_sim, list_to_remove, m0, rand_num, do_random):
    # Get the index of the employee that matches the name
    idx = indices[name]

    # Get the pairwsie similarity scores of all employees with that employee
    sim_scores = list(enumerate(cosine_sim[idx]))
    
    # Sort the employees based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the employee indices
    emp_indices = []
    emp_sims = []
    if do_random:
        group_num = rand_num 
    else:
        group_num = num + 1
    for i in sim_scores:
        if (len(emp_indices) == group_num): break
        if i[0] not in list_to_remove and i[0] != idx:
            emp_indices.append(i[0])
            emp_sims.append(i[1])

    # Return the top group_num most similar people not already paired
    result = m0.iloc[emp_indices]
    result = result.assign(Similarity = emp_sims) # still need this?
    return result 

import random 
# choose partners from list of top similar people from get_recommendations
def get_random(mylist, num, do_random): # num = number of people per group
    if (len(mylist) >= num):
        inds = list(mylist.index)
        result = pd.DataFrame(columns=features)
        if do_random:
            rand_inds = random.sample(inds, num-1)
            for i in rand_inds:
                result = pd.concat([result, mylist[mylist.index == i]], sort=False)
        else:
            for i in range(0, num-1):
                result = pd.concat([result, mylist[mylist.index == inds[i]]], sort=False)
    else:
        result = mylist
    return result

# loop through list of people and pair people not already paired
def get_pairs(emplist, indices, cosine_sim, m0, num, rand_num, do_random):
    pairs = []
    list_to_remove = []
    
    for e in emplist:
        if indices[e] not in list_to_remove:
            partner = list(get_random(get_recommendations(e, indices, cosine_sim, list_to_remove, m0, rand_num, do_random), num, do_random)['index'])
            name0 = e
            pair = [name0]
            
            list_to_remove.append(indices[e])
            for p in partner:
                pair.append(p)
                list_to_remove.append(indices[p])

            pairs.append(pair)
            
            list_to_remove.sort(reverse=True)
    return pairs

df = convert_csv_to_matrix(csv, num)
print(df)
# print("Done")
df.to_csv('testing.csv', index=False)