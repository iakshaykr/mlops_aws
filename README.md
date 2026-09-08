# MLOps House Price Prediction Service

A production-ready FastAPI-based machine learning inference service for predicting house prices in Indian cities. This project demonstrates modern MLOps practices with containerization, AWS integration, structured logging, and prediction auditing.

## 🎯 What This Project Does

- Exposes a REST API that accepts house property details (city, area, bedrooms, bathrooms, age, parking)
- Runs inference using a pre-trained scikit-learn regression model
- Logs all predictions with structured logging for observability
- Audits every prediction to S3 for compliance and analysis
- Supports both local development and AWS ECS deployment
- Handles multiple Indian cities via lookup table mapping

## 📊 Tech Stack

- Language: Python 3.11
- Framework: FastAPI 0.116.1 + Uvicorn 0.35.0
- ML/Data: scikit-learn 1.5.2, pandas 2.2.3, numpy 1.26.4, joblib 1.4.2
- Cloud: AWS S3, ECS, boto3 1.39.14
- Validation: Pydantic 2.11.7
- Containerization: Docker

## 📁 Project Structure

```text
mlops_case_study/
├── .github/
│   └── workflows/
│       └── deploy.yml
├── app/
│   ├── audit.py
│   ├── config.py
│   ├── logger.py
│   ├── main.py
│   ├── models.py
│   ├── predictor.py
│   └── preprocess.py
├── data/
│   └── city_lookup.csv
├── model/
│   └── model.pkl
├── notebook/
│   ├── 01_train_model.ipynb
│   └── train_house_model.ipynb
├── Dockerfile
├── requirements.txt
├── .gitignore
├── README.md
└── tests/
```

### How It Fits Together

1. Request Flow: HTTP POST → `main.py` validates request schema (Pydantic)
2. Preprocessing: `preprocess.py` looks up city ID from `city_lookup.csv`, converts parking bool to int, builds feature vector
3. Inference: `predictor.py` loads model from S3 (AWS mode) or local disk, runs prediction
4. Logging: Structured logs record request, features, prediction, errors at multiple levels
5. Audit Trail: `audit.py` writes every prediction to S3 with timestamp, inputs, and outputs for compliance

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip
- Docker (optional, for containerized deployment)
- AWS credentials (optional, for S3 integration)

### Local Development

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the API:

```bash
uvicorn app.main:app --reload
```

The server runs on `http://127.0.0.1:8000`

3. Test the health endpoint:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status": "UP"}
```

4. Make a prediction:

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Bangalore",
    "area": 1200,
    "bedrooms": 2,
    "bathrooms": 2,
    "house_age": 5,
    "parking": true
  }'
```

Expected response:

```json
{
  "estimated_price": 7250000.5,
  "currency": "INR"
}
```

## 🐳 Docker Deployment

### Build the image

```bash
docker build -t mlops-inference:latest .
```

### Run locally

```bash
docker run -p 8000:8000 mlops-inference:latest
```

### Run with AWS credentials (for S3 access)

```bash
docker run -p 8000:8000 \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  -e ENV=aws \
  -e MODEL_BUCKET=your-model-bucket \
  -e MODEL_KEY=models/model.pkl \
  -e AUDIT_BUCKET=your-audit-bucket \
  mlops-inference:latest
```

## 📡 API Endpoints

### `GET /health`

Health check endpoint for load balancers and monitoring.

Response:

```json
{
  "status": "UP"
}
```

### `POST /predict`

Predicts house price based on property features.

Request body:

```json
{
  "city": "string",
  "area": 1200,
  "bedrooms": 2,
  "bathrooms": 2,
  "house_age": 5,
  "parking": true
}
```

Success response (200):

```json
{
  "estimated_price": 7250000.5,
  "currency": "INR"
}
```

Error response (400 - Unsupported city):

```json
{
  "detail": "Unsupported city: InvalidCity"
}
```

Error response (500 - Unexpected error):

```json
{
  "detail": "Internal Server Error"
}
```

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|---|---:|---|---|
| `ENV` | No | `local` | Deployment environment (`local` or `aws`) |
| `MODEL_BUCKET` | Yes (if AWS) | - | S3 bucket containing the model |
| `MODEL_KEY` | Yes (if AWS) | - | S3 object key for the model file |
| `AUDIT_BUCKET` | Yes (if AWS) | - | S3 bucket for storing prediction audits |
| `LOOKUP_KEY` | No | `city_lookup.csv` | S3 object key for city lookup file |

### Local Development Notes

- By default, the app uses local files: `model/model.pkl` and `data/city_lookup.csv`
- No AWS credentials are required for local testing
- Set `ENV=aws` to enable S3 downloads and S3 audit logging

## 📝 Logging

The application uses structured logging via Python's `logging` module:

- INFO: Request received, features processed, successful predictions
- WARNING: Validation errors (unsupported cities)
- ERROR/EXCEPTION: Unexpected errors with full stack traces

Example log output:

```text
INFO:root:Incoming request: {'city': 'Bangalore', 'area': 1200, ...}
INFO:root:Processed features: [1, 1200, 2, 2, 5, 1]
INFO:root:Inference Success | city=Bangalore, area=1200, ... predicted_price=7250000.5
```

## 🔐 Audit Trail

Every prediction is logged to S3 in JSON format at:

```text
s3://{AUDIT_BUCKET}/predictions/{YEAR}/{MM}/{DD}/{uuid}.json
```

Example audit record:

```json
{
  "timestamp": "2026-09-09T10:30:45.123456",
  "input": {
    "city": "Bangalore",
    "area": 1200,
    "bedrooms": 2,
    "bathrooms": 2,
    "house_age": 5,
    "parking": true
  },
  "prediction": {
    "estimated_price": 7250000.5,
    "currency": "INR"
  }
}
```

## 🧪 Testing

The `tests/` directory is currently empty. Contribute unit tests for:

- Request validation (Pydantic models)
- City lookup edge cases (unknown cities, case sensitivity)
- Prediction output format and ranges
- Error handling (missing environment variables, S3 failures)
- Audit logging

## 📚 Model Training

Two Jupyter notebooks are included for reference:

- `notebook/01_train_model.ipynb` – Primary model training pipeline
- `notebook/train_house_model.ipynb` – Alternative training approach

Both notebooks build the scikit-learn regression model saved as `model/model.pkl`.

## 🚢 Production Deployment

The `.github/workflows/deploy.yml` workflow automates:

1. Build the Docker image
2. Test the application
3. Deploy to AWS ECS
4. Approval gate for production promotion

Triggered on pushes to the `main` branch.

## 🔄 Roadmap & TODOs

- Complete `app/config.py` with Pydantic settings for centralized config management
- Add unit tests in `tests/` directory (pytest + fixtures)
- Add model versioning and A/B testing support
- Implement request caching layer for identical predictions
- Add monitoring/metrics export (Prometheus)
- Support model hot-reload without restarting container
- Add request rate limiting
- Expand supported cities in `data/city_lookup.csv`

## 📄 License

[Specify your license here, e.g., MIT, Apache 2.0]

## 👤 Author

[Your Name / Organization]

---

## ❓ FAQ

**Q: What cities are supported?**
A: Check `data/city_lookup.csv` for the current list. The API performs case-insensitive matching.

**Q: Can I use this without AWS?**
A: Yes! Keep `ENV=local` (default) and ensure local files exist: `model/model.pkl` and `data/city_lookup.csv`.

**Q: How do I add a new city?**
A: Add a row to `data/city_lookup.csv` with a unique `id` and `city` name. Restart the app to reload.

**Q: What happens if S3 is unavailable?**
A: In AWS mode, the first request will fail if the model/lookup file hasn't been cached locally. Subsequent requests use the cached files in `/tmp/`.

**Q: How are predictions audited?**
A: Every prediction is automatically written to S3 in JSON format with timestamp, inputs, and outputs.
