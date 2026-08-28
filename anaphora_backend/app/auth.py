"""
No production auth for the MVP (PRD section 5 explicitly excludes it).
Instead: the frontend generates a UUID client-side on first load and sends
it as a header on every request. We upsert a User row on first sight so
every conversation/blueprint is still tied to a stable identity across the
demo session, without a login flow.
"""
from fastapi import Header, Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import User


def get_current_user(
    x_anaphora_user_id: str = Header(..., alias="X-Anaphora-User-Id"),
    db: Session = Depends(get_db),
) -> User:
    user = db.get(User, x_anaphora_user_id)
    if not user:
        user = User(id=x_anaphora_user_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
