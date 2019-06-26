# Import Pandas
import pandas as pd

# Import NumPy
import numpy as np

# Load Dating Profiles Metadata
metadata = pd.read_csv('../data/profiles.csv')


id_numbers = np.arange(0,metadata.shape[0])


idx=0
metadata.insert(loc=idx, column='id_number', value=id_numbers)


m0 = metadata[['id_number','age','body_type','diet','drinks','education','essay0','essay1',
      'essay2','essay3','essay4','essay5','essay6','essay7','essay8','essay9',
      'ethnicity','height','job','location','offspring','orientation','pets',
      'religion','sex','sign','smokes','speaks','status']]


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
features = ['id_number','age','body_type','diet','drinks','education','essay0','essay1',
      'essay2','essay3','essay4','essay5','essay6','essay7','essay8','essay9',
      'ethnicity','height','job','location','offspring','orientation','pets',
      'religion','sex','sign','smokes','speaks','status']
m1 = m0.copy()
for feature in features:
    m1[feature] = m0[feature].apply(clean_data)



m1['score'] = m1['id_number'] + " " +  m1['age'] + " " + m1['body_type'] + " " + m1['diet'] + " " + m1['drinks'] + " " + m1['education'] + " " + m1['essay0'] + " " + m1['essay1'] + " " + m1['essay2'] + " " + m1['essay3'] + " " + m1['essay4'] + " "+ m1['essay5'] + " " + m1['essay6'] + " " + m1['essay7'] + " " + m1['essay8'] + " " + m1['essay9'] + " " + m1['ethnicity'] + " " + m1['height'] + " " + m1['job'] + " " + m1['location'] + " " + m1['offspring'] + " " + m1['orientation'] + " " + m1['pets'] + " " + m1['religion'] + " " + m1['sex'] + " " + m1['sign'] + " " + m1['smokes'] + " " + m1['speaks'] + " " + m1['status']


m1.head(3)


from sklearn.feature_extraction.text import TfidfVectorizer
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(m1['score'])
from sklearn.metrics.pairwise import linear_kernel
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
indices = pd.Series(m1.index, index=m0['id_number']).drop_duplicates()


def get_recommendations(idx, cosine_sim=cosine_sim):

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



print('done')

print(get_recommendations(2))