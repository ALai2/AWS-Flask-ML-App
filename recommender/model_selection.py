import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier 

features = ['Employee Name','State','Zip','DOB','Sex','Date of Hire','Department','Position']
# primary = 'Employee Name'
# groupby = 'Department'
# weights = {'Employee Name': 3}
# num = 3
csv = '../human-resources/HRDataset_v9.csv'

# Load Employees Metadata
metadata = pd.read_csv(csv)
m0 = metadata[features]

# input features and output target
raw_data = metadata.drop('target', axis=1) # get just features
y = metdata['target'] # get target value

# modify raw_data to get X
X = raw_data

# X, y = np.arange(10).reshape((5,2)), range(5) 

# 20% of data goes into test set, 80% into training set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# somehow have way to change weights
cl = RandomForestClassifier(n_estimators=900, n_jobs=-1) # select model to create
cl.fit(X_train, y_train)
rfaccur = cl.score(X_test, y_test)
print(rfaccur)

# y = cl.predict(X_test)
# 1. create model using data csv
# 2. predict using input csv
# use cross validation?