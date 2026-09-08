# import joblib

# model = joblib.load("model/model.pkl")


# def predict(features):
#     prediction = model.predict([features])
#     probability = model.predict_proba([features])

#     return prediction[0], probability.max()

import os
import boto3
import joblib

MODEL_BUCKET = os.getenv("MODEL_BUCKET")
MODEL_KEY = os.getenv("MODEL_KEY")

LOCAL_MODEL = "/tmp/model.pkl"

s3 = boto3.client("s3")

if not os.path.exists(LOCAL_MODEL):

    s3.download_file(
        MODEL_BUCKET,
        MODEL_KEY,
        LOCAL_MODEL
    )

model = joblib.load(LOCAL_MODEL)


def predict(features):

    prediction = model.predict([features])[0]

    return round(float(prediction), 2)
