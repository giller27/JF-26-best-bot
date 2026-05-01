# src/utils/exporter.py
import csv
import io
from fastapi.responses import StreamingResponse

async def export_users_to_csv():
    users = await db.db.registrations.find().to_list(None)
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "ПІБ", "Телефон", "Університет", "Джерело", "Дата"])
    
    for u in users:
        writer.writerow([
            u["user_id"], u["full_name"], u["phone"], 
            u["university"], u.get("source", "-"), u["registered_at"]
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=registrations.csv"}
    )