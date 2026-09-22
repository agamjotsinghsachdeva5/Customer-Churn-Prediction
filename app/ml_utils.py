# import joblib
# import pandas as pd
# import shap
# import os
# from app.feature_engineer import FeatureEngineer
# import __main__
# __main__.FeatureEngineer = FeatureEngineer


# # ---- Load the pipeline once when the app starts ----
# MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'pipeline.pkl')
# pipeline = joblib.load(MODEL_PATH)

# # Split out the pieces we need individually for SHAP
# feature_engineer = pipeline.named_steps['feature_engineer']
# preprocessor = pipeline.named_steps['preprocessor']
# classifier = pipeline.named_steps['classifier']

# # Build the SHAP explainer once at startup (fast for tree models)
# # We need a small transformed background sample - but for a live API,
# # TreeExplainer can work directly off the trained classifier
# explainer = shap.TreeExplainer(classifier)

# # Your chosen threshold from Colab
# BEST_THRESHOLD = 0.28


# def predict_customer(customer_dict: dict):
#     """
#     Takes raw customer data (matching your 19 original columns),
#     runs it through feature engineering + preprocessing,
#     returns prediction, probability, and SHAP explanation.
#     """
#     # Convert single customer dict into a one-row DataFrame
#     df = pd.DataFrame([customer_dict])

#     # Step 1: feature engineering (TenureGroup, TotalServices, ExpectedTotal, ChargeDifference)
#     df_engineered = feature_engineer.transform(df)

#     # Step 2: preprocessing (ordinal + scaling + one-hot)
#     X_transformed = preprocessor.transform(df_engineered)

#     # Step 3: prediction
#     proba = classifier.predict_proba(X_transformed)[0][1]
#     prediction = int(proba >= BEST_THRESHOLD)

#     # Step 4: SHAP explanation
#     shap_values = explainer(X_transformed)
#     # Get feature names after preprocessing (needed to label SHAP values)
#     raw_feature_names = preprocessor.get_feature_names_out()
# # Strip the sklearn step prefix (e.g. "onehot__Contract" -> "Contract") for cleaner display
#     feature_names = [name.split('__', 1)[-1] for name in raw_feature_names]
#     # Get feature names after preprocessing (needed to label SHAP values)


#     # shap_values.values shape depends on binary vs multiclass - handle both
#     values = shap_values.values[0]
#     if values.ndim > 1:  # multi-output case
#         values = values[:, 1]  # class 1 = churn

#     base_value = shap_values.base_values[0]
#     if hasattr(base_value, '__len__'):
#         base_value = base_value[1]

#     shap_explanation = [
#         {"feature": name, "shap_value": float(val), "feature_value": float(X_transformed[0][i]) if hasattr(X_transformed, '__getitem__') else None}
#         for i, (name, val) in enumerate(zip(feature_names, values))
#     ]

#     # Sort by absolute SHAP impact, descending
#     shap_explanation.sort(key=lambda x: abs(x['shap_value']), reverse=True)

#     return {
#         "churn_probability": round(float(proba), 4),
#         "prediction": "Churn" if prediction == 1 else "Not Churn",
#         "threshold_used": BEST_THRESHOLD,
#         "shap_explanation": shap_explanation[:10],  # top 10 drivers
#         "base_value": round(float(base_value), 4)
#     }
import joblib
import pandas as pd
import shap
import os

from app.feature_engineer import FeatureEngineer
import __main__
__main__.FeatureEngineer = FeatureEngineer

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'pipeline.pkl')
pipeline = joblib.load(MODEL_PATH)

feature_engineer = pipeline.named_steps['feature_engineer']
preprocessor = pipeline.named_steps['preprocessor']
classifier = pipeline.named_steps['classifier']

explainer = shap.TreeExplainer(classifier)

BEST_THRESHOLD = 0.28

ONEHOT_COLS = ['gender', 'Partner', 'Dependents', 'PhoneService', 'PaperlessBilling',
               'MultipleLines', 'InternetService', 'PaymentMethod',
               'OnlineSecurity', 'OnlineBackup', 'DeviceProtection',
               'TechSupport', 'StreamingTV', 'StreamingMovies', 'TenureGroup']

FRIENDLY_LABELS = {
    'tenure': 'Tenure (months)',
    'MonthlyCharges': 'Monthly Charges',
    'TotalCharges': 'Total Charges',
    'ExpectedTotal': 'Expected Total Charges',
    'ChargeDifference': 'Charge Gap (Expected vs Actual)',
    'Contract': 'Contract Type',
    'SeniorCitizen': 'Senior Citizen',
    'TotalServices': 'Total Services Subscribed',
    'gender': 'Gender',
    'Partner': 'Has Partner',
    'Dependents': 'Has Dependents',
    'PhoneService': 'Phone Service',
    'PaperlessBilling': 'Paperless Billing',
    'MultipleLines': 'Multiple Lines',
    'InternetService': 'Internet Service',
    'PaymentMethod': 'Payment Method',
    'OnlineSecurity': 'Online Security',
    'OnlineBackup': 'Online Backup',
    'DeviceProtection': 'Device Protection',
    'TechSupport': 'Tech Support',
    'StreamingTV': 'Streaming TV',
    'StreamingMovies': 'Streaming Movies',
    'TenureGroup': 'Tenure Group',
}


def _original_feature_info(encoded_name, df_engineered):
    """Map an encoded SHAP feature name back to its original column
    and human-readable raw value, instead of a scaled number."""
    if encoded_name in df_engineered.columns:
        raw_value = df_engineered[encoded_name].values[0]
        label = FRIENDLY_LABELS.get(encoded_name, encoded_name)

        if encoded_name == 'SeniorCitizen':
            raw_value = 'Yes' if int(raw_value) == 1 else 'No'

        return label, raw_value

    matched_col = None
    for col in ONEHOT_COLS:
        prefix = col + '_'
        if encoded_name.startswith(prefix) and (matched_col is None or len(col) > len(matched_col)):
            matched_col = col

    if matched_col:
        raw_value = df_engineered[matched_col].values[0]
        label = FRIENDLY_LABELS.get(matched_col, matched_col)
        return label, raw_value

    return encoded_name, None


def predict_customer(customer_dict: dict):
    df = pd.DataFrame([customer_dict])

    df_engineered = feature_engineer.transform(df)
    X_transformed = preprocessor.transform(df_engineered)

    proba = classifier.predict_proba(X_transformed)[0][1]
    prediction = int(proba >= BEST_THRESHOLD)

    shap_values = explainer(X_transformed)
    raw_feature_names = preprocessor.get_feature_names_out()
    feature_names = [name.split('__', 1)[-1] for name in raw_feature_names]

    values = shap_values.values[0]
    if values.ndim > 1:
        values = values[:, 1]

    base_value = shap_values.base_values[0]
    if hasattr(base_value, '__len__'):
        base_value = base_value[1]

    shap_explanation = []
    for name, val in zip(feature_names, values):
        label, raw_value = _original_feature_info(name, df_engineered)

        if isinstance(raw_value, float):
            raw_value = round(raw_value, 2)

        shap_explanation.append({
            "feature": label,
            "raw_value": raw_value,
            "shap_value": round(float(val), 4),
            "direction": "increases" if val > 0 else "decreases"
        })

    # Dedupe by label - keep the strongest-impact row per original column
    dedup = {}
    for item in shap_explanation:
        key = item['feature']
        if key not in dedup or abs(item['shap_value']) > abs(dedup[key]['shap_value']):
            dedup[key] = item
    shap_explanation = sorted(dedup.values(), key=lambda x: abs(x['shap_value']), reverse=True)

    return {
        "churn_probability": round(float(proba), 4),
        "prediction": "Churn" if prediction == 1 else "Not Churn",
        "threshold_used": BEST_THRESHOLD,
        "base_value": round(float(base_value), 4),
        "shap_explanation": shap_explanation[:8],
        "customer_summary": {
            "tenure": int(df_engineered['tenure'].values[0]),
            "monthly_charges": float(df_engineered['MonthlyCharges'].values[0]),
            "total_charges": float(df_engineered['TotalCharges'].values[0]),
            "contract": customer_dict.get('Contract'),
            "internet_service": customer_dict.get('InternetService'),
            "total_services": int(df_engineered['TotalServices'].values[0]),
        }
    }