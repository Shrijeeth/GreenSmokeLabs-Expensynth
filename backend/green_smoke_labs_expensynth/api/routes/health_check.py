from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def root():
    return {"success": True, "message": "Expensynth API is up and running!"}
