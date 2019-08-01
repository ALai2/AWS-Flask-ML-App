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

# 270 students --> around 17 minutes
# 187 students --> around 8 minutes
# reduce amount of predictions needed to be made by not predicting unwanted pairs
# create new file for pairing model predictions

use_index = True 
# use_index = False 

# Define a TF-IDF Vectorizer Object. Remove all english stop words such as 'the', 'a'
tfidf = TfidfVectorizer(stop_words = 'english') # stop words include numbers so what to do about Grad Year?

features = ['Name','Gender','Major','Grad Year','Class 1','Class 2','Class 3','Class 4','Interest 1','Interest 2','Study Habits','Hometown','Campus Location','Race','Preferences']
training_features = ['Name','Gender','Major','Grad Year','Classes 1','Interests','Study Habits','Hometown','Campus Location','Race','Preferences']
second_features = ['Name','Classes 2']

classes = ['Class 1','Class 2','Class 3','Class 4']
second_classes = classes + ['Class 5','Class 6','Class 7','Class 8']
interests = ['Interest 1','Interest 2']
combine = {'Classes 1': classes, 'Classes 2': second_classes, 'Interests': interests}

primary = 'Name'
# csv = 'Test Classes Extended.csv'
csv = 'Prof Clarkson Test Data - Sheet1 (1).csv'
training_csv = "?"
output = 'target'

filename = 'finalized_model.sav'
model_choice = {1: 'first_model.sav', 2: 'second_model.sav'}
create_2_model = False 


def get_similarity(first, second): # return similarity between two strings
    
    if not first or not second or first is None or second is None:
        return 0.0
    if len(first) == 1 or len(second) == 1:
        if first == second: return 1.0 
        else: return 0.0 
    if first == second:
        return 1.0 
    
    df = pd.DataFrame([first, second])
    # print(df)

    #Construct the required TF-IDF matrix by fitting and transforming the data
    tfidf_matrix = tfidf.fit_transform(df[0])

    # Compute the cosine similarity matrix
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    return cosine_sim[0][1]
    
    # print(first)
    # print(second)
    # df1 = pd.DataFrame(first)
    # df2 = pd.DataFrame(second)
    # tm1 = tfidf.fit_transform(df1[0])
    # tm2 = tfidf.fit_transform(df2[0])

    # cosine_sim = linear_kernel(tm1, tm2)
    # result = [ cosine_sim[i][i] for i in range(0, len(cosine_sim)) ]
    # return result 

def load_prediction(df, m0, model_num, combine):
    soup_data = []
    if model_num == 1:
        allfeatures = training_features
    elif model_num == 2:
        allfeatures = second_features

    for i in df.iterrows(): # loop through df rows and acquire similarity ratios
        mylist = i[1]['group'].split("; ")
        name_list = []
        for m in mylist:
            if use_index:
                index = int(m)
                name_list.append(index)
            else:
                if create_2_model:
                    group = m.split(", ")
                    for g in group:
                        name_list.append(m0['index'][m0['Name'] == g].iloc[0])
                else:
                    name_list.append(m0['index'][m0['Name'] == m].iloc[0])
        
        loop_list = [[], []]
        
        soups = [ i[1]['group'] ]

        '''
        for feature in [x for x in training_features if x != primary]:
            for j in range(0,2):
                if feature == 'Classes':
                    loop_list[j].append(" ".join(m0[m0[primary] == name_list[j]][c].iloc[0] for c in classes))
                elif feature == 'Interests':
                    loop_list[j].append(" ".join(m0[m0[primary] == name_list[j]][i].iloc[0] for i in interests))
                else:
                    loop_list[j].append(m0[m0[primary] == name_list[j]][feature].iloc[0])
        
        soups += get_similarity(loop_list[0], loop_list[1]) 
        '''
        
        if not create_2_model:
            for feature in [x for x in allfeatures if x != primary]:
                mylist = []
                for j in range(0,2):
                    if feature in combine:
                        mylist.append(" ".join(m0[m0['index'] == name_list[j]][i].iloc[0] for i in combine[feature]))
                    else:
                        mylist.append(m0[m0['index'] == name_list[j]][feature].iloc[0])
                soups.append(get_similarity(mylist[0], mylist[1]))  
        else:
            for feature in [x for x in second_features if x != primary]:
                mylist = []
                half = len(name_list) / 2
                acc = []
                for k in range(0, len(name_list)):
                    if k == half:
                        mylist.append(" ".join(acc))
                        acc = []
                    if feature in combine:
                        acc.append(" ".join(m0[m0['index'] == name_list[k]][i].iloc[0] for i in combine[feature]))
                    else:
                        acc.append(m0[m0['index'] == name_list[j]][feature].iloc[0])
                mylist.append(" ".join(acc))
                soups.append(get_similarity(mylist[0], mylist[1]))  
        
        
        soup_data.append(soups)

    df_soup = pd.DataFrame(soup_data, columns=allfeatures)
    return df_soup 

def create_model(model_num):
    metadata = pd.read_csv(csv)
    m0 = metadata[features].reset_index()
    m0 = ci.clean_df(m0, features, primary, classes)

    '''
    # Load training data
    training = pd.read_csv(training_csv)
    metadata = training[['group','target]]
    '''
    # will later change to data in training_csv
    if model_num == 1:
        data = [["Maya; Maia", 2], ["Maya; Stanley", 3], ["Evan; Jen", 5],["Jordyn; Tom", 7]]
        allfeatures = training_features
    elif model_num == 2:
        data = [["Maya, Maia; Evan, Jen", 2],["Jordyn, Tom; Rebecca, Frank", 7]]
        allfeatures = second_features
    metadata = pd.DataFrame(data, columns=['group','target'])

    # modify df to get X
    df = metadata.drop(output, axis=1) # get just features
    y = metadata[output] # get target values

    # df is features to be predicted
    # m0 is information about people
    df_soup = load_prediction(df, m0, model_num, combine)

    # don't need feature scaling, all similarity numbers are between 0 and 1
    X = df_soup[[x for x in allfeatures if x != primary]]

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
    filename = model_choice[model_num]
    # save the model (cl) to disk
    pickle.dump(cl, open(filename, 'wb'))
    return None 

# HELLO!!!!!!!!!!!!!!!!!-------------------------------------------------
# create_model(2)

def make_prediction(df_soup, X_test, model_num):
    # load the model from disk
    filename = model_choice[model_num]
    cl = pickle.load(open(filename, 'rb'))
    # dataframe of numerical features for prediction
    predictions = cl.predict(X_test)
    X_test = X_test.assign(Prediction = predictions)
    X_test = X_test.sort_values(by='Prediction', ascending=False)

    index_list = list(X_test.index)
    name_list = df_soup[['Name']].iloc[index_list]
    X_test = X_test.assign(Name = name_list)

    cols = X_test.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    X_test = X_test[cols]
    
    return X_test

def construct_similarity(m0, model_num, combine):
    if use_index:
        names = list(m0.index)
    else:
        names = list(m0['Name'])
    length = len(names)

    # create psudo-similarity matrix
    pairs = list(itertools.combinations(names, 2))
    matrix = np.eye(length, length)
    
    data = []
    for (one, two) in pairs:
        if use_index:
            data.append([str(one) + "; " + str(two)])
        else:
            data.append([one + "; " + two])

    df = pd.DataFrame(data, columns=['group'])

    df_soup = load_prediction(df, m0, model_num, combine)
    if model_num == 1:
        features = training_features
    elif model_num == 2:
        features = second_features
    
    X_test = df_soup[[x for x in features if x != primary]]

    predictions = make_prediction(df_soup, X_test, model_num)
    
    # loop through df rows and acquire similarity ratios
    for p in predictions.iterrows():
        [one, two] = p[1]['Name'].split("; ")
        
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

# # first = ['female', 'anthropology', '2021', 'anthr1400 anthr1200 anthr1300 cs 4620', 'pizza plays', 'istartmyassignmentsclosertothedeadline.', 'virginia', 'northcampus(other)', '4', '']
# # second = ['prefer not to specify', 'urbanandregionalstudies', '2021', 'cs4420 astro1101 cs4320 engl 1100', 'writing history of literature', 'istartmyassignmentsclosertothedeadline.', 'iowa', 'northcampus(other)', '6', '']
# first = ['one','two','three four']
# second = ['one','asdfasd','asdfasd']
# df1 = pd.DataFrame(first)
# df2 = pd.DataFrame(second)
# tm1 = tfidf.fit_transform(df1[0])
# tm2 = tfidf.fit_transform(df2[0])
# print(tm1.shape[1])
# print(tm2.shape[1])

# # print(tm1)
# # print(tm2)
# cosine_sim = linear_kernel(tm1, tm2)
# result = [ cosine_sim[i][i] for i in range(0, len(cosine_sim)) ]
# print(result) 