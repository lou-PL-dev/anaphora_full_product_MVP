"""Deterministic canonicalizer used by offline endpoint regression scripts."""
from app.schemas import CanonicalBlueprintResult


def canonicalize_without_llm(rows):
    grouped = {}
    for row in rows:
        key = (row.perspective, row.category, row.label.strip().casefold())
        if key not in grouped:
            grouped[key] = {
                "perspective": row.perspective,
                "category": row.category,
                "label": row.label,
                "evidence_ids": [],
            }
        grouped[key]["evidence_ids"].append(row.id)
    ideal_labels = [
        item["label"] for item in grouped.values()
        if item["perspective"] == "IDEAL_PARTNER"
    ]
    narrative = "You are drawn to someone " + ", ".join(ideal_labels) + "." if ideal_labels else ""
    return CanonicalBlueprintResult(signals=list(grouped.values()), narrative=narrative)
