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
# print(m1.head(3))

#Import TfIdfVectorizer from scikit-learn
from sklearn.feature_extraction.text import TfidfVectorizer

#Define a TF-IDF Vectorizer Object. Remove all english stop words such as 'the', 'a'
tfidf = TfidfVectorizer(stop_words='english')

#Replace NaN with an empty string
# m['score'] = m['score'].fillna('')

#Construct the required TF-IDF matrix by fitting and transforming the data
tfidf_matrix = tfidf.fit_transform(m1['score'])

#Output the shape of tfidf_matrix
# tfidf_matrix.shape

# Import linear_kernel
from sklearn.metrics.pairwise import linear_kernel

# Compute the cosine similarity matrix
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

#Construct a reverse map of indices and employee names
indices = pd.Series(m1.index, index=m0['Employee Name']).drop_duplicates()

# Function that takes in movie title as input and outputs most similar movies
def get_recommendations(name, cosine_sim=cosine_sim):
    # Get the index of the employee that matches the name
    idx = indices[name]

    # Get the pairwsie similarity scores of all employees with that employee
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort the employees based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the 10 most similar employees
    sim_scores = sim_scores[1:11]
    # print(sim_scores)

    # Get the employee indices
    emp_indices = [i[0] for i in sim_scores]
    emp_sims = [i[1] for i in sim_scores]

    # Return the top 10 most similar employee
    result = m0.iloc[emp_indices]
    result = result.assign(Similarity = emp_sims)
    return result 

print(get_recommendations('Brown, Mia'))