# Import Pandas
import pandas as pd

# Import TfIdfVectorizer from scikit-learn
from sklearn.feature_extraction.text import TfidfVectorizer

# Import linear_kernel
from sklearn.metrics.pairwise import linear_kernel

import json # for testing

# Define a TF-IDF Vectorizer Object. Remove all english stop words such as 'the', 'a'
tfidf = TfidfVectorizer(stop_words='english')

# features
features = ['Name','Major','Class 1','Class 2','Class 3','Class 4','Interest 1','Interest 2','Interest 3','Hometown','Hometype']
primary = 'Name'
# groupby = 'Major'
groupby = None
weights = {'Name': 0, 'Major': 30, 'Class 1': 20, 'Class 2': 20, 'Class 3': 20, 'Class 4': 20, 'Interest 1': 12, 'Interest 2': 12, 'Interest 3': 12, 'Hometown': 18, 'Hometype': 0}
num = 2
csv = 'Test Classes Extended.csv'
# csv = 'ProfileInfo.csv'

# minimize number of global variables
def convert_csv_to_matrix(csv, num):
    # Load Employees Metadata
    metadata = pd.read_csv(csv)
    m0 = metadata[features]
    m0 = m0.reset_index()
    group_dict = {}
    matches = []
    ones = []

    def func_pairs(group):
        # Apply clean_data function to your features and create soup
        m1 = group.copy()
        # print(group)
        m1['score'] = ""
        for feature in features:
            m1[feature] = group[feature].apply(ci.clean_data)
            
            if feature in ['Major', 'Class 1', 'Class 2', 'Class 3', 'Class 4', 'Hometown']:
                m1[feature] = m1[feature].apply(ci.replace_space)
            # print(m1[feature])
            
            if feature in weights:
                for i in range(weights[feature]):
                    m1['score'] = m1['score'] + " " + m1[feature]
            else:
                m1['score'] = m1['score'] + " " + m1[feature]
            
        #Construct the required TF-IDF matrix by fitting and transforming the data
        tfidf_matrix = tfidf.fit_transform(m1['score'])

        # Compute the cosine similarity matrix
        cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

        #Construct a reverse map of indices and employee names
        # indices = pd.Series(m1.index, index=group[primary]).drop_duplicates()
        indices = pd.Series(m1.index, index=m1['index']).drop_duplicates()
        return get_pairs(group['index'].sample(frac=1), indices, cosine_sim, group, num)
        # return get_pairs(group[primary].sample(frac=1), indices, cosine_sim, group, num)

    if groupby is not None:
        courses = m0[groupby].unique() # list of all unique department names
        
        for course in courses:
            group = (m0[m0[groupby] == course]).reset_index()
            # keep track of groups with only one member
            
            if len(group) == 1:
                ones.append(group)
            else:
                matches = matches + func_pairs(group)
        
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
            df = pd.DataFrame(columns=features)
            for one in ones:
                df = df.append(one, sort=False)
            df = df.reset_index().drop('level_0', axis=1)
            matches = matches + func_pairs(df)
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
    num = 0
    for i in sim_scores:
        if (num == 2): break
        if (num != 0):
            if i[0] not in list_to_remove:
                emp_indices.append(i[0])
                emp_sims.append(i[1])
                num = num + 1
        else:
            num = num + 1

    # Return the top 10 most similar employee not already paired
    result = m0.iloc[emp_indices]
    result = result.assign(Similarity = emp_sims) # still need this?
    return result 

import random 
def get_random(mylist, num): # num = number of people per group
    if (len(mylist) > num):
        inds = list(mylist.index)
        rand_inds = random.sample(inds, num-1)
        result = pd.DataFrame()
        for i in rand_inds:
            result = pd.concat([result, mylist[mylist.index == i]])
    else:
        result = mylist
    return result

# semi-greedy algorithm
def get_pairs(emplist, indices, cosine_sim, m0, num):
    # pairs = []
    list_to_remove = []
    pairs = pd.DataFrame()
    for e in emplist:
        
        if indices[e] not in list_to_remove:
            partner = list(get_random(get_recommendations(e, indices, cosine_sim, list_to_remove, m0), num)['index'])
            # name0 = m0[primary][m0['index'] == e].iloc[0] + " " + str(e)
            pairs = pairs.append(m0[m0['index'] == e].iloc[0])
            
            name0 = m0[m0['index'] == e].iloc[0]
            pair = [name0]
            list_to_remove.append(indices[e])
            for p in partner:
                # pair.append(m0[primary][m0['index'] == p].iloc[0] + " " + str(p))
                pairs = pairs.append(m0[m0['index'] == p].iloc[0])
                list_to_remove.append(indices[p])

            new = pd.DataFrame([pair])
            pairs = pairs.append(['pair'], sort=False)
            pairs.append(pair)
            list_to_remove.sort(reverse=True)
 
    return pairs

# print(convert_csv_to_matrix(csv, num))
df = convert_csv_to_matrix(csv, num)
print(df)
df.to_csv('testing.csv', index=False)