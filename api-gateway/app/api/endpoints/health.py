from fastapi import APIRouter
from http import HTTPStatus

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": HTTPStatus.OK, "message": "API Gateway is running"}
