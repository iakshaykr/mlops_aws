import os
import json
import uuid
from datetime import datetime

import boto3

s3 = boto3.client("s3")

AUDIT_BUCKET = os.getenv("AUDIT_BUCKET")


def save_audit(request, status, prediction=None, error=None):

    now = datetime.utcnow()

    key = (
        f"audit/"
        f"{now.year}/"
        f"{now.month:02d}/"
        f"{now.day:02d}/"
        f"{uuid.uuid4()}.json"
    )

    payload = {
        "timestamp": now.isoformat(),

        "status": status,

        "input": {
            "city": request.city,
            "area": request.area,
            "bedrooms": request.bedrooms,
            "bathrooms": request.bathrooms,
            "house_age": request.house_age,
            "parking": request.parking
        }
    }

    if prediction is not None:
        payload["prediction"] = {
            "estimated_price": prediction,
            "currency": "INR"
        }

    if error is not None:
        payload["error"] = error

    s3.put_object(
        Bucket=AUDIT_BUCKET,
        Key=key,
        Body=json.dumps(payload, indent=4),
        ContentType="application/json"
    )

    return key
