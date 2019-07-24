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
tfidf = TfidfVectorizer(stop_words='english')

# features
# features = ['Name', 'Major','Class 1','Class 2','Class 3','Class 4','Interest 1','Interest 2','Interest 3','Hometown','Hometype']
# weights = {'Name': 0, 'Major': 30, 'Class 1': 20, 'Class 2': 20, 'Class 3': 20, 'Class 4': 20, 'Interest 1': 12, 'Interest 2': 12, 'Interest 3': 12, 'Hometown': 18, 'Hometype': 0}
features = ['Name','Gender','Major','Grad Year','Class 1','Class 2','Class 3','Class 4','Interest 1','Interest 2','Study Habits','Hometown','Campus Location','Race','Preferences']
weights = {'Name': 0, 'Gender': 0, 'Major': 5, 'Grad Year': 7, 'Class 1': 10, 'Class 2': 10, 'Class 3': 10, 'Class 4': 10, 'Interest 1': 6, 'Interest 2': 6, 'Study Habits': 15, 'Hometown': 3, 'Campus Location': 14, 'Race': 0, 'Preferences': 0}
# Clarkson weights
# S = 1.8 C, L = 1.5 C, I = 0.8 C, H = 0.6 C, G = 0.5 C, M = 0.3 C
# weights = {'Name': 0, 'Gender': 0, 'Major': 5, 'Grad Year': 7, 'Class 1': 10, 'Class 2': 10, 'Class 3': 10, 'Class 4': 10, 'Interest 1': 6, 'Interest 2': 6, 'Study Habits': 15, 'Hometown': 3, 'Campus Location': 14, 'Race': 0, 'Preferences': 0}

primary = 'Name'
# groupby = 'Race'
groupby = None

num = 2
# csv = 'Test Classes Extended.csv'
csv = 'Prof Clarkson Test Data - Sheet1 (1).csv'
# csv = 'ProfileInfo.csv'
# use_model = True 
use_model = False 
pair_groups = False 
# pair_groups = True 
random = True    
rand_num = 3

# minimize number of global variables
def convert_csv_to_matrix(csv, num):
    # Load data from csv
    metadata = pd.read_csv(csv)
    m0 = metadata[features]
    m0 = m0.reset_index()
    group_dict = {}
    if pair_groups:
        matches = {}
    else:
        matches = pd.DataFrame(columns=features + ['index'])
    ones = []

    def func_pairs(group):
        # apply clean_df function to features
        m1 = group.copy()
        m1 = ci.clean_df(m1, features, primary)
        
        if use_model:
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

        return get_pairs(group['index'].sample(frac=1), indices, cosine_sim, group, num)

    if groupby is not None:
        courses = m0[groupby].unique() # list of all unique department names
        
        for course in courses:
            group = (m0[m0[groupby] == course]).reset_index().drop('level_0', axis=1)
            # keep track of groups with only one member

            if len(group) == 1:
                ones.append(group)
            else:
                if pair_groups:
                    matches[course] = func_pairs(group)
                else:
                    matches = pd.concat([matches, func_pairs(group)], sort=False)
        
        if len(ones) != 0:
            if len(ones) == 1:
                if pair_groups:
                    matches['Outcast'] = ones.pop(0)
                else:
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
                if pair_groups:
                    matches['Other'] = func_pairs(df)
                else:
                    matches = pd.concat([matches, func_pairs(df)], sort=False)
    else:
        matches = func_pairs(m0)
    
    return matches

# Function that takes in movie title as input and outputs most similar movies
def get_recommendations(name, indices, cosine_sim, list_to_remove, m0):
    # Get the index of the employee that matches the name
    idx = indices[name]

    # Get the pairwsie similarity scores of all employees with that employee
    sim_scores = list(enumerate(cosine_sim[idx]))
    
    # Sort the employees based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the employee indices
    emp_indices = []
    emp_sims = []
    for i in sim_scores:
        if (len(emp_indices) == rand_num): break
        if i[0] not in list_to_remove and i[0] != idx:
            emp_indices.append(i[0])
            emp_sims.append(i[1])

    # Return the top 10 most similar employee not already paired
    result = m0.iloc[emp_indices]
    result = result.assign(Similarity = emp_sims) # still need this?
    return result 

import random 
def get_random(mylist, num): # num = number of people per group
    if (len(mylist) > num):
        inds = list(mylist.index)
        if random:
            rand_inds = random.sample(inds, num-1)
            result = pd.DataFrame(columns=features)
            for i in rand_inds:
                result = pd.concat([result, mylist[mylist.index == i]], sort=False)
        else:
            for i in range(0, num):
                result = pd.concat([result, mylist[mylist.index == i]], sort=False)
    else:
        result = mylist
    return result

# semi-greedy algorithm
def get_pairs(emplist, indices, cosine_sim, m0, num):
    if pair_groups:
        pairs = []
    else:
        pairs = pd.DataFrame(columns=features + ['index'])
    list_to_remove = []
    
    for e in emplist:
        if indices[e] not in list_to_remove:
            partner = list(get_random(get_recommendations(e, indices, cosine_sim, list_to_remove, m0), num)['index'])
            if pair_groups:
                name0 = m0[primary][m0['index'] == e].iloc[0] + " " + str(e)
                pair = [name0]
            else:
                name0 = m0[m0['index'] == e].iloc[0]
                pairs = pairs.append(m0[m0['index'] == e].iloc[0])
            
            list_to_remove.append(indices[e])
            for p in partner:
                if pair_groups:
                    pair.append(m0[primary][m0['index'] == p].iloc[0] + " " + str(p))
                else:
                    pairs = pairs.append(m0[m0['index'] == p].iloc[0])
                list_to_remove.append(indices[p])

            if pair_groups:
                pairs.append(pair)
            else:
                data = [['-'] * (len(features)+1)]
                extra = pd.DataFrame(data, columns=features + ['index'])
                pairs = pd.concat([pairs, extra], sort=False)
            
            list_to_remove.sort(reverse=True)
    return pairs

if pair_groups:
    print(convert_csv_to_matrix(csv, num))
    # create groups using pairs from each group
else:
    df = convert_csv_to_matrix(csv, num)
    print(df)
    df.to_csv('testing.csv', index=False)