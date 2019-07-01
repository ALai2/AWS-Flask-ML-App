# https://www.geeksforgeeks.org/python-pandas-dataframe-groupby/

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
features = ['Employee Name','State','Zip','DOB','Sex','Date of Hire','Department','Position']
primary = 'Employee Name'
groupby = 'Department'

# Function to convert all strings to lower case and strip names of spaces
def clean_data(x):
    if isinstance(x, list):
        return [str.lower(i).strip() for i in x]
    else:
        #Check if item exists. If not, return empty string
        if isinstance(x, str):
            return str.lower(x).strip()
        else:
            return ''

# minimize number of global variables
def convert_csv_to_matrix(csv, num):
    # Load Employees Metadata
    metadata = pd.read_csv(csv)
    m0 = metadata[features]

    group_dict = {}
    courses = m0[groupby].unique() # list of all unique department names
    for course in courses:
        group = (m0[m0[groupby] == course]).reset_index()
        print(group)

        # Apply clean_data function to your features and create soup
        m1 = group.copy()
        m1['score'] = ""
        for feature in features:
            m1[feature] = group[feature].apply(clean_data)
            m1['score'] = m1['score'] + " " + m1[feature]

        #Construct the required TF-IDF matrix by fitting and transforming the data
        tfidf_matrix = tfidf.fit_transform(m1['score'])

        # Compute the cosine similarity matrix
        cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

        #Construct a reverse map of indices and employee names
        indices = pd.Series(m1.index, index=group[primary]).drop_duplicates()
        
        # print(group)
        group_dict[course] = get_pairs(group[primary].sample(frac=1), indices, cosine_sim, group, num)
        print(course + ": " + json.dumps(group_dict[course]) + "\n")
    
    # return get_pairs(m0[primary].sample(frac=1), indices, cosine_sim, m0, num)
    return group_dict

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
        if (num == 11): break
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
    pairs = []
    list_to_remove = []
    for e in emplist:
        if not (indices[e] in list_to_remove):
            partner = list(get_random(get_recommendations(e, indices, cosine_sim, list_to_remove, m0), num)[primary])
            
            pair = [e]
            list_to_remove.append(indices[e])
            for p in partner:
                pair.append(p)
                list_to_remove.append(indices[p])
            pairs.append(pair)
            
            list_to_remove.sort(reverse=True)
    return pairs

convert_csv_to_matrix('../human-resources/HRDataset_v9.csv', 3)