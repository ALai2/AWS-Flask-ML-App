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

def replace_space(x):
    if isinstance(x, str):
        return str.lower(x).replace(" ", "")
    else:
        return ''

def trim_str(x):
    if isinstance(x, str):
        return x.strip()
    else:
        return ''

import pandas as pd 
# Load data from csv and organize
def clean_df(m0, features, primary):
    for feature in [x for x in features if x != primary]:
        m0[feature] = m0[feature].apply(clean_data)
                
        if feature in ['Major', 'Class 1', 'Class 2', 'Class 3', 'Class 4', 'Hometown']:
            m0[feature] = m0[feature].apply(replace_space)
    m0[primary] = m0[primary].apply(trim_str)
    return m0