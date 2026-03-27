from fastapi import APIRouter
from app.discovery.sofascore_discovery import get_all_relevant_match_ids_sync

router = APIRouter(prefix="/discovery", tags=["discovery"])

@router.get("/matches")
def get_all_matches():
    return {"match_ids": get_all_relevant_match_ids_sync()}
