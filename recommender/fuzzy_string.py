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

soup = m1[['score']]

#Construct a reverse map of indices and employee names
indices = pd.Series(m1.index, index=m0['Employee Name']).drop_duplicates()

# Function that takes in movie title as input and outputs most similar movies
def get_recommendations(name):
    # Get the index of the employee that matches the name
    idx = indices[name]
    [self_soup] = soup[soup.index == idx]['score']
    
    score_list = soup[soup.index != idx]['score']

    # Get the pairwsie similarity scores of all employees with that employee
    # and return the 5 most similar employees
    from fuzzywuzzy import process # pip install fuzzywuzzy # pip install python-Levenshtein
    ratios = process.extract(self_soup, score_list)
    zip_ratios = list(zip(*ratios))
    sim_scores = list(zip_ratios[1])
    emp_indices = list(zip_ratios[2])
    
    result = m0.iloc[emp_indices]
    result = result.assign(Similarity = sim_scores)
    return result 

print(get_recommendations('Brown, Mia'))