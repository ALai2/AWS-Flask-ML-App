import pandas as pd
import numpy as np
# X, y = np.arange(10).reshape((5,2)), range(5) 
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier 

# Import TfIdfVectorizer from scikit-learn
from sklearn.feature_extraction.text import TfidfVectorizer

# Import linear_kernel
from sklearn.metrics.pairwise import linear_kernel

# Define a TF-IDF Vectorizer Object. Remove all english stop words such as 'the', 'a'
tfidf = TfidfVectorizer(stop_words='english')

features = ['Name','Major','Class 1','Class 2','Class 3','Class 4','Interest 1','Interest 2','Interest 3','Hometown','Hometype']
# features = ['Employee Name','State','Zip','DOB','Sex','Date of Hire','Department','Position']
primary = 'Name'
# groupby = 'Major'
groupby = None
weights = {'Name': 0, 'Major': 30, 'Class 1': 20, 'Class 2': 20, 'Class 3': 20, 'Class 4': 20, 'Interest 1': 12, 'Interest 2': 12, 'Interest 3': 12, 'Hometown': 18, 'Hometype': 0}
num = 2
csv = 'Test Classes Extended.csv'
output = 'target'

# Load student data
metadata = pd.read_csv(csv)
m0 = metadata[features]

# input features and output target
# raw_data = metadata.drop(output, axis=1) # get just features
# y = metdata[output] # get target value
# need names from training set?

def get_similarity(first, second): # return similarity between two strings
    df = pd.DataFrame()
    df = df.append([first, second])
    
    #Construct the required TF-IDF matrix by fitting and transforming the data
    tfidf_matrix = tfidf.fit_transform(df[0])

    # Compute the cosine similarity matrix
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    return cosine_sim[0][1]

features = ['Name','feature','test']
data = [["Name1", "playing with trains", "playing with fire", "Name2", "playing", "TESTING"], ["ONE","MATH2110", "CS2110","TWO", "first", "second"]]
df = pd.DataFrame(data, columns=['Name1','feature1','test1','Name2', 'feature2','test2'])
print(df)

# what if group has more than two people?
# get student info from different csv than training set?
soup_data = []
for i in df.iterrows(): # loop through df rows and acquire similarity ratios
    soups = []
    for feature in features:
        first = i[1][feature + str(1)] # first = m0[m0['Name'] == name1][feature]
        second = i[1][feature + str(2)]
        if feature != primary:
            soups.append(get_similarity(first, second))
        else:
            soups.append(first + ", " + second)
    soup_data.append(soups)
new = pd.DataFrame(soup_data, columns=features)
print(new)

'''
soup_data = []
for i in df.iterrows():
    first_name = i[1][name1]
    second_name = i[1][name2]
    soups = [first_name, second_name]
    for feature in features:
        if feature != "Name":
            first = m0[m0['Name'] == first_name][feature]
            second = m0[m0['Name'] == second_name][feature]
            soups.append(get_similarity(first, second))
    soup_data.append(soups)
new = pd.DataFrame(soup_data, columns=(['name1','name2'] + features))

''' #  use only numbers, no names in training dataframe

'''
# modify raw_data to get X
# get similarity of strings from cosine
X = raw_data
# https://stackoverflow.com/questions/15173225/calculate-cosine-similarity-given-2-sentence-strings 
# http://blog.christianperone.com/2013/09/machine-learning-cosine-similarity-for-vector-space-models-part-iii/ 

# 20% of data goes into test set, 80% into training set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# somehow have way to change weights
cl = RandomForestClassifier(n_estimators=900, n_jobs=-1) # select model to create
cl.fit(X_train, y_train)
rfaccur = cl.score(X_test, y_test)
print(rfaccur)

y = cl.predict(X_test)
# get names
# get info of people with names
# get similarity ratios and create dataframe with values
# predict and get outputs
'''

'''
import pickle

# save the model to disk
model = cl
filename = 'finalized_model.sav'
pickle.dump(model, open(filename, 'wb'))

# load the model from disk
loaded_model = pickle.load(open(filename, 'rb'))
result = loaded_model.score(X_test, Y_test)
print(result)
'''