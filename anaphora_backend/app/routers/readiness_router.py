from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_user
from ..models import User
from ..schemas import ReadinessResponse
from ..readiness import compute_readiness

router = APIRouter(prefix="/readiness", tags=["readiness"])


@router.get("", response_model=ReadinessResponse)
def get_readiness(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pct, breakdown = compute_readiness(db, user.id)
    return ReadinessResponse(readiness_pct=pct, breakdown=breakdown)
