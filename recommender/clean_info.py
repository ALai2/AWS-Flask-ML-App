import keywords_dict as kd 

def key_replace(x):
    if isinstance(x, str):
        keywords = kd.get_keywords()
        for k in keywords:
            if str.lower(x).strip() in keywords[k]:
                return k
        return x 
    else:
        return ''

'''
def course_replace(x):
    if isinstance(x, str):
        x = format_course(x)
        courses = kd.get_courses()
        if x in courses: ?????
            return courses[x]
        return x
    else:
        return ''
'''

def format_course(x):
    txt = str.upper(x.replace(" ", ""))
    for i in range(len(txt)-1, -1, -1):
        if not txt[i].isdigit():
            return txt[0:i+1] + " " + txt[i+1:]

# import re 
# def course_match(x):
#     pattern = '([A-Za-z]+)[\s]*([\d]+)'
#     if re.search(pattern, x):
#         return True 
#     return False 
# print(course_match("E2NGRD 2110"))

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
                
        if feature in ['Major', 'Class 1', 'Class 2', 'Class 3', 'Hometown','Study Habits','Campus Location']:
            m0[feature] = m0[feature].apply(replace_space)
    m0[primary] = m0[primary].apply(trim_str)
    return m0