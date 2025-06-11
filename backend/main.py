from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1 import uploads

app = FastAPI(title="ProductPulse API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(uploads.router, prefix="/api/v1/uploads", tags=["uploads"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the ProductPulse API!"}