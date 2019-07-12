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
    # print(df_soup)

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
    y = metadata[output] # get target value

    # df is features to be predicted
    # m0 is information about people
    df_soup = load_prediction(df, m0)

    # don't need feature scaling, all similarity numbers are between 0 and 1
    X = df_soup[[x for x in training_features if x != primary]]

    # later on don't split the dataset
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

    return df_soup, X_test
    # return cl?

'''
# Load prediction data (to create df_soup)
# df is pairings in dataframe format
m0 = clean_df(prediction_csv)
df_soup = load_prediction(df, m0)
# have list of names and information about people
'''
# df_soup, X_test = create_model()

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

# print(make_prediction(df_soup, X_test))

def construct_similarity(m0):
    names = list(m0['Name'])
    length = len(names)

    # create psudo-similarity matrix
    pairs = list(itertools.combinations(names, 2))
    matrix = np.eye(length, length)
    
    # list.index(element)
    data = []
    for (one, two) in pairs:
        data.append([one + ", " + two])
    df = pd.DataFrame(data, columns=['group'])

    df_soup = load_prediction(df, m0)
    # print(df_soup)
    X_test = df_soup[[x for x in training_features if x != primary]]

    predictions = make_prediction(df_soup, X_test)
    
    for p in predictions.iterrows(): # loop through df rows and acquire similarity ratios
        [one, two] = p[1]['Name'].split(", ")
        index1 = names.index(one)
        index2 = names.index(two)
        pred = p[1]['Prediction'] / 10
        matrix[index1][index2] = pred 
        matrix[index2][index1] = pred
    
    return matrix 
    # print(matrix) # <-- new cosine_sim matrix

    # make pairs using similarity matrix
    # from sklearn.cluster import KMeans
    # group_list = KMeans(n_clusters=60, init="k-means++").fit_predict(matrix)
    # # print(group_list)

    # mylists = [ [] for i in range(60) ]
    # for i in range(len(group_list)):
    #     group = group_list[i]
    #     mylists[group].append(m0.iloc[i][primary])
    
    # print(mylists)

    '''
    remainder = len(names) % num
    if remainder == 1:
        return 1 # make one num + 1 group and then group rest in num groups
    elif remainder != 0:
        return 2 # group remainder and then group rest in num groups
    # make groups with num people
    pairs = list(itertools.combinations(names, remainder))
    '''
    # return None  
# metadata = pd.read_csv(csv)
# m0 = metadata[features]
# m0 = ci.clean_df(m0, features, primary) # need some way to split for groupby
# print(construct_similarity(m0))
'''
# links about random forests classifier
https://www.datacamp.com/community/tutorials/random-forests-classifier-python 
https://stackabuse.com/random-forest-algorithm-with-python-and-scikit-learn/ 
https://towardsdatascience.com/random-forest-in-python-24d0893d51c0 
https://dataaspirant.com/2017/06/26/random-forest-classifier-python-scikit-learn/ 
https://medium.com/machine-learning-101/chapter-5-random-forest-classifier-56dc7425c3e1 
https://jakevdp.github.io/PythonDataScienceHandbook/05.08-random-forests.html 
'''
