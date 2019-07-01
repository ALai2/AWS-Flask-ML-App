# spectral clustering better for smaller number of groups
# Import Pandas
import pandas as pd

# Import TfIdfVectorizer from scikit-learn
from sklearn.feature_extraction.text import TfidfVectorizer

# Import linear_kernel
from sklearn.metrics.pairwise import linear_kernel

from sklearn.cluster import SpectralClustering
import numpy as np 

# Define a TF-IDF Vectorizer Object. Remove all english stop words such as 'the', 'a'
tfidf = TfidfVectorizer(stop_words='english')

# features
features = ['Employee Name','State','Zip','DOB','Sex','Date of Hire','Department','Position']
primary = 'Employee Name'

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

    # Apply clean_data function to your features and create soup
    m1 = m0.copy()
    m1['score'] = ""
    for feature in features:
        m1[feature] = m0[feature].apply(clean_data)
        m1['score'] = m1['score'] + " " + m1[feature]
    
    #Replace NaN with an empty string
    # m['score'] = m['score'].fillna('')

    #Construct the required TF-IDF matrix by fitting and transforming the data
    tfidf_matrix = tfidf.fit_transform(m1['score'])

    # Compute the cosine similarity matrix
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    
    total = int(len(m1) / num)
    group_list = SpectralClustering(n_clusters=total, n_init=100, affinity='nearest_neighbors', n_neighbors=num).fit_predict(cosine_sim)

    mylists = [ [] for i in range(total) ]
    for i in range(len(group_list)):
        group = group_list[i]
        mylists[group].append(m0.iloc[i]['Employee Name'])
    
    return mylists


print(convert_csv_to_matrix('../human-resources/HRDataset_v9.csv', 2))