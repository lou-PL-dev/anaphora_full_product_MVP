"""One-time cleanup for Blueprints created before canonical evidence storage.

Examples (from anaphora_backend/):
    python canonicalize_blueprints.py --all
    python canonicalize_blueprints.py --user-id <uuid>

Each member is committed independently. If one model call fails, that member's
existing Blueprint remains intact and the script continues with the others.
"""
import argparse

from sqlalchemy import text

from app.blueprint_canonicalizer import ensure_evidence_backfill, rebuild_blueprint
from app.database import Base, SessionLocal, engine
from app.models import BlueprintEvidence, BlueprintSignal, Candidate, User


def _ensure_schema() -> None:
    if engine.dialect.name == "postgresql":
        Base.metadata.create_all(bind=engine)
        with engine.begin() as conn:
            conn.execute(text(
                "ALTER TABLE blueprint_signals ADD COLUMN IF NOT EXISTS evidence_ids JSON"
            ))
    else:
        tables = [table for table in Base.metadata.sorted_tables if table.name != Candidate.__tablename__]
        Base.metadata.create_all(bind=engine, tables=tables)
        with engine.begin() as conn:
            columns = {
                row[1] for row in conn.execute(text("PRAGMA table_info(blueprint_signals)"))
            }
            if "evidence_ids" not in columns:
                conn.execute(text(
                    "ALTER TABLE blueprint_signals ADD COLUMN evidence_ids JSON"
                ))


def _has_blueprint_data(db, user_id: str) -> bool:
    return bool(
        db.query(BlueprintSignal.id).filter(BlueprintSignal.user_id == user_id).first()
        or db.query(BlueprintEvidence.id).filter(BlueprintEvidence.user_id == user_id).first()
    )


def canonicalize_user(user_id: str) -> tuple[int, int]:
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if user is None:
            raise ValueError("User not found")
        if not _has_blueprint_data(db, user_id):
            return 0, 0
        preserved = ensure_evidence_backfill(db, user_id)
        signals = rebuild_blueprint(db, user)
        db.commit()
        return preserved, len(signals)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Rebuild deduplicated Relationship Blueprints")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--all", action="store_true", help="Canonicalize every member with Blueprint data")
    target.add_argument("--user-id", help="Canonicalize one member UUID")
    args = parser.parse_args()

    _ensure_schema()
    if args.user_id:
        user_ids = [args.user_id]
    else:
        db = SessionLocal()
        try:
            user_ids = [user_id for (user_id,) in db.query(User.id).all()]
        finally:
            db.close()

    processed = skipped = failed = 0
    for user_id in user_ids:
        try:
            preserved, signal_count = canonicalize_user(user_id)
            if preserved == 0 and signal_count == 0:
                skipped += 1
                continue
            processed += 1
            print(f"Canonicalized {user_id}: preserved={preserved}, signals={signal_count}")
        except Exception as exc:
            failed += 1
            print(f"FAILED {user_id}: {exc}")

    print(f"Done: processed={processed}, skipped={skipped}, failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
