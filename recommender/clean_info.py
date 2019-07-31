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

'''
def format_course(x):
    txt = str.upper(x.replace(" ", ""))
    for i in range(len(txt)-1, -1, -1):
        if not txt[i].isdigit():
            return txt[0:i+1] + " " + txt[i+1:]
    return txt 

def course_replace(x):
    if isinstance(x, str):
        x = format_course(x)
        courses = kd.get_courses()
        for c in courses:
            if x in courses[c]:
                return c
        return x
    else:
        return ''

def replace_df(m0):
    for feature in ['Interest 1','Interest 2']:
        m0[feature] = m0[feature].apply(key_replace)
    for feature in ['Class 1','Class 2','Class 3','Class 4']:
        m0[feature] = m0[feature].apply(course_replace)
    return m0
'''

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
    return x.replace(" ", "")

def trim_str(x):
    return x.strip()

import pandas as pd 
# Load data from csv and organize
def clean_df(m0, features, primary, i_classes):
    for feature in [x for x in features if x != primary]:
        m0[feature] = m0[feature].apply(clean_data)
                
        if feature in i_classes + ['Major', 'Hometown','Study Habits','Campus Location']:
            m0[feature] = m0[feature].apply(replace_space)
    m0[primary] = m0[primary].apply(trim_str)
    return m0