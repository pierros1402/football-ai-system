from fastapi import APIRouter
from app.services.stats_service import (
    get_full_match_data,
    get_normalized_match,
)

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/full/{match_id}")
def full_match_endpoint(match_id: int):
    return get_full_match_data(match_id)


@router.get("/normalized/{match_id}")
def normalized_match_endpoint(match_id: int):
    return get_normalized_match(match_id)
