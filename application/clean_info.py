import keywords_dict as kd
keywords = kd.get_keywords()

def key_replace(x):
    if isinstance(x, str):
        for k in keywords:
            if str.lower(x).strip() in keywords[k]:
                return k
        return x 
    else:
        return ''

# Function to convert all strings to lower case and strip names of spaces
def clean_data(x):
    if isinstance(x, list):
        return [str.lower(i).strip() for i in x]
    else:
        #Check if item exists. If not, return empty string
        if isinstance(x, str): # check dictionary
            return str.lower(x).strip()
        elif isinstance(x, int):
            return str(x)
        else:
            return ''

def replace_space(x):
    return (x.replace(" ", "")).replace(",", " ")

def trim_str(x):
    return x.strip()

import pandas as pd 
# Load data from csv and organize
def clean_df(m0, features, clean, key):
    for feature in features:
        m0[feature] = m0[feature].apply(clean_data)
                
        if feature in clean:
            m0[feature] = m0[feature].apply(replace_space)
        
        if feature in key:
            m0[feature] = m0[feature].apply(key_replace)
    return m0

# mylist = ['one','two','three']
# mylist.append(mylist[len(mylist)-1] + " " + mylist[len(mylist)-2])
# mylist.remove(mylist[len(mylist)-1])
# print(mylist)