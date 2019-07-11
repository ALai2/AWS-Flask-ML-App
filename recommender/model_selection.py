import pandas as pd
import numpy as np
# X, y = np.arange(10).reshape((5,2)), range(5) 
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier 

# Import TfIdfVectorizer from scikit-learn
from sklearn.feature_extraction.text import TfidfVectorizer

# Import linear_kernel
from sklearn.metrics.pairwise import linear_kernel

import itertools
import clean_info as ci 
import pickle 

# Define a TF-IDF Vectorizer Object. Remove all english stop words such as 'the', 'a'
tfidf = TfidfVectorizer(stop_words='english')

features = ['Name','Major','Class 1','Class 2','Class 3','Class 4','Interest 1','Interest 2','Interest 3','Hometown','Hometype']
training_features = ['Name','Major','Classes','Interests','Hometown','Hometype']
classes = ['Class 1','Class 2','Class 3','Class 4']
interests = ['Interest 1','Interest 2','Interest 3']
primary = 'Name'
# groupby = 'Major'
groupby = None
weights = {'Name': 0, 'Major': 30, 'Class 1': 20, 'Class 2': 20, 'Class 3': 20, 'Class 4': 20, 'Interest 1': 12, 'Interest 2': 12, 'Interest 3': 12, 'Hometown': 18, 'Hometype': 0}
num = 2
csv = 'Test Classes Extended.csv'
training_csv = "?"
output = 'target'
filename = 'finalized_model.sav'

# Load data from csv and organize
def clean_df(csv):
    metadata = pd.read_csv(csv)
    m0 = metadata[features]

    for feature in [x for x in features if x != primary]:
        m0[feature] = m0[feature].apply(ci.clean_data)
                
        if feature in ['Major', 'Class 1', 'Class 2', 'Class 3', 'Class 4', 'Hometown']:
            m0[feature] = m0[feature].apply(ci.replace_space)
    m0[primary] = m0[primary].apply(ci.trim_str)
    return m0

def get_similarity(first, second): # return similarity between two strings
    if first is None or second is None:
        return 0.0
    
    df = pd.DataFrame()
    df = df.append([first, second])
    
    #Construct the required TF-IDF matrix by fitting and transforming the data
    tfidf_matrix = tfidf.fit_transform(df[0])

    # Compute the cosine similarity matrix
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    return cosine_sim[0][1]

def create_model():
    m0 = clean_df(csv)

    '''
    # Load training data
    training = pd.read_csv(training_csv)
    metadata = training[features]
    '''

    # will later change to data in training_csv
    data = [["Pam, Shane", 2], ["Pam, Brad, Chad", 3], ["Jackson, Pedro, Sam", 5],["Joshua, Joshua2", 7]]
    metadata = pd.DataFrame(data, columns=['group','target'])

    # modify df to get X
    df = metadata.drop(output, axis=1) # get just features
    y = metadata[output] # get target value

    soup_data = []
    for i in df.iterrows(): # loop through df rows and acquire similarity ratios
        mylist = i[1]['group'].split(", ")
        # be careful of the way the group is inputted
        # split by commas and then use strip?
        pairs = list(itertools.combinations(mylist, 2))
        soups = [i[1]['group']]
        for feature in [x for x in training_features if x != primary]:
            acc = 0.0
            for p in pairs:
                name1 = p[0]
                name2 = p[1]
                
                # use index or name? is duplicate names a big problem? or use netid for this?
                index1 = m0.index[m0[primary] == name1][0]
                index2 = m0.index[m0[primary] == name2][0]
                # name1 = m0['Name'][m0.index == index1].iloc[0]
                
                first = ""
                second = ""
                if feature == 'Classes':
                    for c in classes:
                        first += " " + m0[m0[primary] == name1][c].iloc[0]
                        second += " " + m0[m0[primary] == name2][c].iloc[0]
                elif feature == 'Interests':
                    for i in interests:
                        first += " " + m0[m0[primary] == name1][i].iloc[0]
                        second += " " + m0[m0[primary] == name2][i].iloc[0]
                else:
                    first = m0[m0[primary] == name1][feature].iloc[0]
                    second = m0[m0[primary] == name2][feature].iloc[0]
                    
                # get average similarity of pairs
                acc += get_similarity(first, second)
            soups.append(acc / len(pairs))
        soup_data.append(soups)
    df_soup = pd.DataFrame(soup_data, columns=training_features)
    print(df_soup)

    # don't need feature scaling, all similarity numbers are between 0 and 1
    X = df_soup[[x for x in training_features if x != primary]]

    # 20% of data goes into test set, 80% into training set
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5)

    # change metrics to increase accuracy, need more data for supervised learning
    cl = RandomForestClassifier(n_estimators=900, n_jobs=-1) # select model to create
    cl.fit(X_train, y_train)
    rfaccur = cl.score(X_test, y_test)
    # print(rfaccur)
    # print(X_test)

    # save the model (cl) to disk
    pickle.dump(cl, open(filename, 'wb'))

    return df_soup, X_test

'''
# Load prediction data
pred = pd.read_csv(prediction_csv)
metadata = pred[features]
# have list of names and information about people
'''
df_soup, X_test = create_model()

def make_prediction(df_soup, X_test):
    '''
    # https://machinelearningmastery.com/save-load-machine-learning-models-python-scikit-learn/ 
    '''
    # load the model from disk
    cl = pickle.load(open(filename, 'rb'))
    # result = loaded_model.score(X_test, Y_test)
    # print(result)
    
    predictions = cl.predict(X_test)
    X_test = X_test.assign(Prediction = predictions).sort_index()
    index_list = list(X_test.index)
    name_list = df_soup[['Name']].iloc[index_list]
    X_test = X_test.assign(Name = name_list)

    cols = X_test.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    X_test = X_test[cols]
    print(X_test)
    
    return None

make_prediction(df_soup, X_test)

'''
# https://www.datacamp.com/community/tutorials/random-forests-classifier-python 
# https://stackabuse.com/random-forest-algorithm-with-python-and-scikit-learn/ 
# https://towardsdatascience.com/random-forest-in-python-24d0893d51c0 
# https://dataaspirant.com/2017/06/26/random-forest-classifier-python-scikit-learn/ 
# https://medium.com/machine-learning-101/chapter-5-random-forest-classifier-56dc7425c3e1 
# https://jakevdp.github.io/PythonDataScienceHandbook/05.08-random-forests.html 
'''

# df = df.sort_values(by='Prediction', ascending=False)

'''
feature_imp = pd.Series(clf.feature_importances_,index=iris.feature_names).sort_values(ascending=False)
print(feature_imp) # feature importance
'''
# predict new data
# also make new pairings for predicted data?

# use algorithm similar to work_with_duplicates to create pairings
# match one person with all pairs
# choose one from top pairings
# remove grouped people from entire list
# choose another person and repeat until finished

# or do all pairs and normalize
# create matrix for KMeans or spectral clustering
