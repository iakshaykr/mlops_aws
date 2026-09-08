# import pandas as pd

# lookup = pd.read_csv("data/city_lookup.csv")


# def preprocess(features):
#     return features

import os
import boto3
import pandas as pd
from fastapi import HTTPException

# Environment
ENV = os.getenv("ENV", "local")

MODEL_BUCKET = os.getenv("MODEL_BUCKET")
LOOKUP_KEY = os.getenv("LOOKUP_KEY", "city_lookup.csv")

# Local file paths
if ENV == "aws":
    LOCAL_LOOKUP = "/tmp/city_lookup.csv"
else:
    LOCAL_LOOKUP = "data/city_lookup.csv"

# Download lookup file from S3 only in AWS
if ENV == "aws":

    s3 = boto3.client("s3")

    if not os.path.exists(LOCAL_LOOKUP):
        print(f"Downloading {LOOKUP_KEY} from S3 bucket {MODEL_BUCKET}")

        s3.download_file(
            MODEL_BUCKET,
            LOOKUP_KEY,
            LOCAL_LOOKUP
        )

        print("Lookup file downloaded")

# Load lookup table
lookup = pd.read_csv(LOCAL_LOOKUP)

print(f"Loaded {len(lookup)} lookup records")


def preprocess(request):
    """
    Convert API request into model features.
    """

    # Case-insensitive lookup
    matches = lookup.loc[
        lookup["city"].str.strip().str.lower()
        == request.city.strip().lower()
    ]

    if matches.empty:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported city: {request.city}"
        )

    city_id = int(matches.iloc[0]["id"])

    parking = 1 if request.parking else 0

    return [
        city_id,
        request.area,
        request.bedrooms,
        request.bathrooms,
        request.house_age,
        parking
    ]
