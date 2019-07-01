# spectral and kmeans clustering better for smaller number of groups
import pandas as pd

# import modules for creating similarity matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# import clustering methods
from sklearn.cluster import SpectralClustering
from sklearn.cluster import KMeans

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

    #Construct the required TF-IDF matrix by fitting and transforming the data
    tfidf_matrix = tfidf.fit_transform(m1['score'])

    # Compute the cosine similarity matrix
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    # cosine_sim[cosine_sim != 1] = cosine_sim[cosine_sim != 1] * 2
    
    total = int(len(m1) / (num*2))
    # group_list = SpectralClustering(n_clusters=total, n_neighbors=10, affinity='precomputed').fit_predict(cosine_sim)
    group_list = KMeans(n_clusters=total, init="k-means++").fit_predict(cosine_sim)

    mylists = [ [] for i in range(total) ]
    for i in range(len(group_list)):
        group = group_list[i]
        mylists[group].append(m0.iloc[i]['Employee Name'])
    
    return mylists

print(convert_csv_to_matrix('../human-resources/HRDataset_v9.csv', 3))