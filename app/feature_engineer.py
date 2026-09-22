from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd

class FeatureEngineer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()

        def tenure_group(t):
            if t <= 12:
                return 'New'
            elif t <= 48:
                return 'Established'
            else:
                return 'Loyal'
        X['TenureGroup'] = X['tenure'].apply(tenure_group)

        service_cols = ['OnlineSecurity', 'OnlineBackup', 'DeviceProtection',
                         'TechSupport', 'StreamingTV', 'StreamingMovies']
        X['TotalServices'] = (X[service_cols] == 'Yes').sum(axis=1)

        X['ExpectedTotal'] = X['tenure'] * X['MonthlyCharges']
        X['ChargeDifference'] = X['ExpectedTotal'] - X['TotalCharges']

        return X