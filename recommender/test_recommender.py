# Import Pandas
import pandas as pd

# Load Employees Metadata
metadata = pd.read_csv('../human-resources/HRDataset_v9.csv')
m0 = metadata[['Employee Name','State','Zip','DOB','Sex','Date of Hire','Department','Position']]

# Function to convert all strings to lower case and strip names of spaces
def clean_data(x):
    if isinstance(x, list):
        return [str.lower(i) for i in x]
    else:
        #Check if item exists. If not, return empty string
        if isinstance(x, str):
            return str.lower(x)
        else:
            return ''

# Apply clean_data function to your features.
features = ['Employee Name','State','Zip','DOB','Sex','Date of Hire','Department','Position']
m1 = m0.copy()
for feature in features:
    m1[feature] = m0[feature].apply(clean_data)

# create soup
m1['score'] = m1['Employee Name'] + " " + m1['State'] + " " + m1['Zip'] + " " + m1['DOB'] + " " + m1['Sex'] + " " + m1['Date of Hire'] + " " + m1['Department'] + " " + m1['Position']

#Import TfIdfVectorizer from scikit-learn
from sklearn.feature_extraction.text import TfidfVectorizer

#Define a TF-IDF Vectorizer Object. Remove all english stop words such as 'the', 'a'
tfidf = TfidfVectorizer(stop_words='english')

#Replace NaN with an empty string
# m['score'] = m['score'].fillna('')

#Construct the required TF-IDF matrix by fitting and transforming the data
tfidf_matrix = tfidf.fit_transform(m1['score'])

# Import linear_kernel
from sklearn.metrics.pairwise import linear_kernel

# Compute the cosine similarity matrix
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

#Construct a reverse map of indices and employee names
indices = pd.Series(m1.index, index=m0['Employee Name']).drop_duplicates()

list_to_remove = []

# Function that takes in movie title as input and outputs most similar movies
def get_recommendations(name, cosine_sim=cosine_sim, list_to_remove=list_to_remove):
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
    result = result.assign(Similarity = emp_sims)
    return result 

import random 
def get_random(mylist):
    group = 2 # number of people per group
    if (len(mylist) > group):
        inds = mylist.index 
        result = pd.DataFrame()
        for i in range(0, group-1):
            rand_ind = random.choice(inds)
            result = pd.concat([result, mylist[mylist.index == rand_ind]])
    else:
        result = mylist
    return result

def get_pairs(emplist):
    pairs = []
    for e in emplist:
        if not (indices[e] in list_to_remove):
            partner = list(get_random(get_recommendations(e))['Employee Name'])
            
            pair = [e]
            list_to_remove.append(indices[e])
            for p in partner:
                pair.append(p)
                list_to_remove.append(indices[p])
            pairs.append(pair)
            
            list_to_remove.sort(reverse=True)
    # print(list_to_remove)
    return pairs

# TODO
def convert_data_to_matrix():
    return None

print(get_pairs(m0['Employee Name'][0:308].sample(frac=1)))
# get_pairs(m0['Employee Name'][0:308].sample(frac=1))