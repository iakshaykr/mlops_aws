from fastapi import FastAPI, HTTPException

from app.models import PredictionRequest
from app.preprocess import preprocess
from app.predictor import predict
from app.logger import logger
from app.audit import save_audit

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "UP"}


@app.post("/predict")
def prediction(request: PredictionRequest):

    try:
        # Log incoming request
        logger.info(f"Incoming request: {request.model_dump()}")

        # Preprocess features
        features = preprocess(request)

        logger.info(f"Processed features: {features}")

        # Model inference
        price = predict(features)

        # Log successful prediction
        logger.info(
            f"Inference Success | "
            f"city={request.city}, "
            f"area={request.area}, "
            f"bedrooms={request.bedrooms}, "
            f"bathrooms={request.bathrooms}, "
            f"house_age={request.house_age}, "
            f"parking={request.parking}, "
            f"predicted_price={price}"
        )

        # Save successful inference to S3
        save_audit(
            request=request,
            status="SUCCESS",
            prediction=price
        )

        return {
            "estimated_price": price,
            "currency": "INR"
        }

    except HTTPException as e:

        # Validation errors
        logger.warning(
            f"Validation Failed | "
            f"Request={request.model_dump()} | "
            f"Reason={e.detail}"
        )

        # Save failed request to S3
        save_audit(
            request=request,
            status="FAILED",
            error=e.detail
        )

        raise

    except Exception as e:

        # Unexpected errors
        logger.exception(
            f"Unexpected Error | "
            f"Request={request.model_dump()}"
        )

        # Save unexpected error to S3
        save_audit(
            request=request,
            status="FAILED",
            error=str(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
