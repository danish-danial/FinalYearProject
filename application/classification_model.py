import numpy as np
import pandas as pd
import joblib

dataset = pd.read_csv("datasets/cleaned_cleveland.csv")

X = dataset.iloc[:, :-1]
y = dataset.iloc[:, -1]

from sklearn.neighbors import KNeighborsClassifier

regressor = KNeighborsClassifier(n_neighbors=21)

regressor.fit(X, y)

joblib.dump(regressor, "classification/model.pkl")

classification_model = joblib.load("classification/model.pkl")

# Test model for returning false result
# print(
#     classification_model.predict([[41, 0, 2, 130, 204, 0, 2, 172, 0, 1.4, 1, 0.0, 3.0]])
# )

#  Test model for returning true result
# print(
#     classification_model.predict([[67, 1, 4, 120, 229, 0, 2, 129, 1, 2.6, 2, 2.0, 3.0]])
# )
