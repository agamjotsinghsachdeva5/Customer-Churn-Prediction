# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from app.schemas import CustomerInput
# from app.ml_utils import predict_customer

# app = FastAPI(title="Customer Churn Prediction API")

# # ---- CORS setup ----
# # Since your frontend is a separate app, the browser will block requests
# # unless this backend explicitly allows it. Update allow_origins once
# # you know your deployed frontend's URL.
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # TODO: replace "*" with your actual frontend URL before final deploy
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse

# @app.get("/")
# def serve_frontend():
#     return FileResponse("static/index.html")

# app.mount("/static", StaticFiles(directory="static"), name="static")


# @app.post("/predict")
# def predict(customer: CustomerInput):
#     try:
#         result = predict_customer(customer.dict())
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.schemas import CustomerInput
from app.ml_utils import predict_customer

app = FastAPI(title="Customer Churn Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "Churn Prediction API is running"}


@app.post("/predict")
def predict(customer: CustomerInput):
    try:
        return predict_customer(customer.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def serve_home():
    return FileResponse("static/index.html")


@app.get("/result")
def serve_result():
    return FileResponse("static/result.html")


app.mount("/static", StaticFiles(directory="static"), name="static")