"""Dashboard route — aggregated data for the main dashboard."""

from fastapi import APIRouter
from store.data_store import store
from engines.vitality_engine import compute_vitality_score
from engines.twin_engine import build_twin
from engines.life_event_engine import predict_life_events
from engines.gps_engine import compute_wealth_gps
from engines.stress_engine import analyze_stress
from engines.advisor_engine import generate_recommendations

router = APIRouter()


@router.get("/dashboard")
def get_dashboard():
    data = store.get_customer()

    vitality = compute_vitality_score(data)
    twin = build_twin(data)
    life_events = predict_life_events(data)
    goals = compute_wealth_gps(data)
    stress = analyze_stress(data)
    recommendations = generate_recommendations(data)

    # Risk alerts from stress signals
    risk_alerts = []
    for signal in stress["signals"]:
        risk_alerts.append({
            "title": signal["title"],
            "description": signal["description"],
            "severity": signal["severity"],
        })

    # Add from advisor recommendations (high priority only)
    for rec in recommendations[:3]:
        if rec["priority"] == "high" and len(risk_alerts) < 5:
            risk_alerts.append({
                "title": rec["title"],
                "description": rec["description"],
                "severity": "medium",
            })

    return {
        "profile": data.profile.model_dump(),
        "vitality": {
            "overall": vitality["overall"],
            "sub_scores": vitality["sub_scores"],
            "labels": vitality["labels"],
        },
        "twin_snapshot": {
            "current": twin["current_state"],
            "projection_1yr": twin["projections"].get("1yr", {}),
        },
        "life_events": life_events[:4],
        "goals": [
            {
                "id": g["id"],
                "name": g["name"],
                "completion_pct": g["completion_pct"],
                "eta": g["eta"],
                "on_track": g["on_track"],
                "target_amount": g["target_amount"],
                "current_amount": g["current_amount"],
            }
            for g in goals
        ],
        "health_timeline": vitality["history"],
        "risk_alerts": risk_alerts[:5],
        "recommendations": [
            {
                "id": r["id"],
                "title": r["title"],
                "description": r["description"],
                "impact": r["impact"],
                "priority": r["priority"],
                "category": r["category"],
                "confidence": r["confidence"],
            }
            for r in recommendations[:5]
        ],
        "stress_level": stress["current_level"],
    }
