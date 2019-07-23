import pandas as pd
import numpy as np

# for creating the ml model
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier 

# import TfIdfVectorizer from scikit-learn
from sklearn.feature_extraction.text import TfidfVectorizer

# import linear_kernel
from sklearn.metrics.pairwise import linear_kernel

import itertools
import clean_info as ci 
import pickle # for saving the ml model

use_index = True 
# use_index = False 

# Define a TF-IDF Vectorizer Object. Remove all english stop words such as 'the', 'a'
tfidf = TfidfVectorizer(stop_words='english')

features = ['Name','Gender','Major','Grad','Class 1','Class 2','Class 3','Class 4','Interest 1','Interest 2','Study Habits','Hometown','Campus Location','Race','Preferences']
training_features = ['Name','Gender','Major','Grad','Classes','Interests','Study Habits','Hometown','Campus Location','Race','Preferences']
classes = ['Class 1','Class 2','Class 3','Class 4']
interests = ['Interest 1','Interest 2']
primary = 'Name'
csv = 'Test Classes Extended.csv'
training_csv = "?"
output = 'target'
filename = 'finalized_model.sav'


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

def load_prediction(df, m0):
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
                
                if use_index:
                    index1 = int(p[0])
                    index2 = int(p[1])
                    name1 = m0['Name'][m0.index == index1].iloc[0]
                    name2 = m0['Name'][m0.index == index2].iloc[0]
                else:
                    name1 = p[0]
                    name2 = p[1]
                
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
    return df_soup 

def create_model():
    metadata = pd.read_csv(csv)
    m0 = metadata[features]
    m0 = ci.clean_df(m0, features, primary)

    '''
    # Load training data
    training = pd.read_csv(training_csv)
    metadata = training[['group','target]]
    '''
    # will later change to data in training_csv
    data = [["Pam, Shane", 2], ["Pam, Brad, Chad", 3], ["Jackson, Pedro, Sam", 5],["Joshua, Joshua2", 7]]
    metadata = pd.DataFrame(data, columns=['group','target'])

    # modify df to get X
    df = metadata.drop(output, axis=1) # get just features
    y = metadata[output] # get target values

    # df is features to be predicted
    # m0 is information about people
    df_soup = load_prediction(df, m0)

    # don't need feature scaling, all similarity numbers are between 0 and 1
    X = df_soup[[x for x in training_features if x != primary]]

    # later on don't split the dataset, just use X and y for fit
    # 20% of data goes into test set, 80% into training set
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5)

    # use regression instead of classifier?
    # change metrics to increase accuracy, need more data for supervised learning
    cl = RandomForestClassifier(n_estimators=900, n_jobs=-1) # select model to create
    cl.fit(X_train, y_train)
    # rfaccur = cl.score(X_test, y_test)
    # print(rfaccur)

    '''
    # add when have real data to create model from
    feature_imp = pd.Series(clf.feature_importances_,index=iris.feature_names).sort_values(ascending=False)
    print(feature_imp) # feature importance
    '''

    # save the model (cl) to disk
    pickle.dump(cl, open(filename, 'wb'))
    return None 

# create_model()

def make_prediction(df_soup, X_test):
    # load the model from disk
    cl = pickle.load(open(filename, 'rb'))
    # dataframe of numerical features for prediction
    predictions = cl.predict(X_test)
    X_test = X_test.assign(Prediction = predictions).sort_index()
    # X_test = X_test.sort_values(by='Prediction', ascending=False)

    index_list = list(X_test.index)
    name_list = df_soup[['Name']].iloc[index_list]
    X_test = X_test.assign(Name = name_list)

    cols = X_test.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    X_test = X_test[cols]
    
    return X_test

def construct_similarity(m0):
    if use_index:
        names = list(m0.index)
    else:
        names = list(m0['Name'])
    length = len(names)

    # create psudo-similarity matrix
    pairs = list(itertools.combinations(names, 2))
    matrix = np.eye(length, length)
    
    # list.index(element)
    data = []
    for (one, two) in pairs:
        if use_index:
            data.append([str(one) + ", " + str(two)])
        else:
            data.append([one + ", " + two])
    df = pd.DataFrame(data, columns=['group'])

    df_soup = load_prediction(df, m0)
    X_test = df_soup[[x for x in training_features if x != primary]]

    predictions = make_prediction(df_soup, X_test)
    
    # loop through df rows and acquire similarity ratios
    for p in predictions.iterrows():
        [one, two] = p[1]['Name'].split(", ")
        
        if use_index:
            index1 = int(one)
            index2 = int(two)
        else:
            index1 = names.index(one)
            index2 = names.index(two)
        pred = p[1]['Prediction'] / 10
        matrix[index1][index2] = pred 
        matrix[index2][index1] = pred
    
    return matrix # psuedo-cosine_sim matrix

# metadata = pd.read_csv(csv)
# m0 = metadata[features]
# m0 = ci.clean_df(m0, features, primary) # need some way to split for groupby
# print(construct_similarity(m0))