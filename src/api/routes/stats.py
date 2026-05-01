# src/api/routes/stats.py
from fastapi import APIRouter, Depends
from src.core.database import db

router = APIRouter(prefix="/api/stats")

@router.get("/summary")
async def get_summary():
    # Агрегація MongoDB
    pipeline = [
        {"$facet": {
            "by_day": [{"$group": {"_id": "$event_days", "count": {"$sum": 1}}}],
            "by_uni": [{"$group": {"_id": "$university", "count": {"$sum": 1}}}],
            "total": [{"$count": "count"}]
        }}
    ]
    results = await db.registrations.aggregate(pipeline).to_list(1)
    return results[0]