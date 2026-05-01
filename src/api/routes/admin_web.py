from fastapi import APIRouter, Request, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from src.core.database import db
from src.core.config import settings
import asyncio

router = APIRouter()
templates = Jinja2Templates(directory="src/api/templates")

@router.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def post_login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "admin": 
        response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="auth", value="super_secret_token")
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "Невірний логін або пароль"})

@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    if request.cookies.get("auth") != "super_secret_token": return RedirectResponse(url="/login", status_code=302)
    
    collection = db.client[settings.DB_NAME]["users"]
    total = await collection.count_documents({})
    
    unis_stat = await collection.aggregate([
        {"$match": {"university": {"$exists": True}}},
        {"$group": {"_id": "$university", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]).to_list(100)

    sources_stat = await collection.aggregate([
        {"$match": {"source": {"$exists": True}}},
        {"$group": {"_id": "$source", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]).to_list(100)

    days_stat = await collection.aggregate([
        {"$match": {"days": {"$exists": True}}},
        {"$group": {"_id": "$days", "count": {"$sum": 1}}}
    ]).to_list(100)

    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "total": total, 
        "unis_stat": unis_stat, 
        "sources_stat": sources_stat,
        "days_stat": days_stat
    })

@router.get("/users", response_class=HTMLResponse)
async def get_users_list(request: Request, university: str = None, source: str = None):
    if request.cookies.get("auth") != "super_secret_token": return RedirectResponse(url="/login", status_code=302)
    
    collection = db.client[settings.DB_NAME]["users"]
    query = {}
    if university: query["university"] = university
    if source: query["source"] = source
        
    users = await collection.find(query).sort("registered_at", -1).to_list(1000)
    unique_unis = await collection.distinct("university")
    
    return templates.TemplateResponse("users.html", {
        "request": request, 
        "users": users, 
        "unique_unis": unique_unis,
        "selected_uni": university,
        "selected_source": source
    })

@router.post("/users/{user_id}/delete")
async def delete_user(user_id: int):
    await db.client[settings.DB_NAME]["users"].delete_one({"user_id": user_id})
    return RedirectResponse(url="/users", status_code=status.HTTP_302_FOUND)

@router.get("/actions", response_class=HTMLResponse)
async def get_actions(request: Request, success: int = None):
    if request.cookies.get("auth") != "super_secret_token": return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("actions.html", {"request": request, "success": success})

# === РОЗСИЛКА ===
@router.post("/broadcast")
async def broadcast_message(request: Request, audience: str = Form(...), text: str = Form(...)):
    if request.cookies.get("auth") != "super_secret_token": 
        return RedirectResponse(url="/login", status_code=302)
    
    # Дістаємо бота напряму з пам'яті сервера (без імпортів!)
    bot = request.app.state.bot 
    
    collection = db.client[settings.DB_NAME]["users"]
    query = {}
    
    if audience == "vntu":
        query = {"university": "ВНТУ"}
    elif audience == "other_buttons":
        query = {"university": {"$in": ["ДонНУ", "ВНМУ", "ВДПУ", "ВНАУ", "ВФЕУ", "ВТЕІ ДТЕУ"]}}
    elif audience == "not_vntu":
        query = {"university": {"$ne": "ВНТУ"}}
        
    users = await collection.find(query).to_list(10000)
    
    count = 0
    
    for user in users:
        # Безпечно дістаємо user_id. Якщо його немає - пропускаємо цього юзера
        user_id = user.get("user_id")
        
        if not user_id:
            print(f"Пропущено запис без ID: {user.get('full_name', 'Невідомий')}")
            continue # Йдемо до наступного
            
        try:
            await bot.send_message(chat_id=user_id, text=text, parse_mode="Markdown")
            count += 1
            await asyncio.sleep(0.05) 
        except Exception as e:
            print(f"Помилка відправки для {user_id}: {e}")
            
    return RedirectResponse(url=f"/actions?success=1", status_code=status.HTTP_302_FOUND)
            
# === ЗАВАНТАЖЕННЯ ФАЙЛІВ (CV) ===
@router.get("/download/{file_id}")
async def download_file(request: Request, file_id: str):
    if request.cookies.get("auth") != "super_secret_token": 
        return RedirectResponse(url="/login", status_code=302)

    # Дістаємо бота з пам'яті
    bot = request.app.state.bot 
    
    try:
        # 1. Просимо у Телеграму інформацію про файл за його ID
        file_info = await bot.get_file(file_id)
        
        # 2. Формуємо пряме URL-посилання на сервери Telegram
        file_url = f"https://api.telegram.org/file/bot{settings.BOT_TOKEN}/{file_info.file_path}"
        
        # 3. Перенаправляємо браузер за цим посиланням (почнеться завантаження)
        return RedirectResponse(url=file_url)
    except Exception as e:
        return HTMLResponse(f"<h3>❌ Помилка: Файл застарів або не знайдений у Telegram. Деталі: {e}</h3>", status_code=404)
