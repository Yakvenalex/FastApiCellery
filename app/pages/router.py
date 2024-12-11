from fastapi import APIRouter, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from app.api.utils import get_file_data
from app.config import redis_client

router = APIRouter(prefix='', tags=['ФРОНТ'])
templates = Jinja2Templates(directory='app/templates')


@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    lifetime_list = [
        {'value': 1, 'text': "1 минута"},
        {'value': 5, 'text': "5 минут"},
        {'value': 15, 'text': "15 минут"},
        {'value': 30, 'text': "30 минут"},
        {'value': 60, 'text': "1 час"},
        {'value': 180, 'text': "3 часа"},
        {'value': 720, 'text': "12 часов"},
        {'value': 1440, 'text': "24 часа"},
    ]

    return templates.TemplateResponse("home.html", {"request": request,
                                                    "lifetime_list": lifetime_list})


@router.get("/view_file/{file_id}", response_class=HTMLResponse)
async def get_file_info(request: Request, file_id: str):
    redis_key = f"file:{file_id}"
    file_info = redis_client.hgetall(redis_key)

    if not file_info:
        return templates.TemplateResponse(
            "file_not_found.html",
            {
                "request": request,
                "file_id": file_id
            }
        )

    # Извлекаем и декодируем значения из Redis
    file_path = file_info.get(b"file_path").decode()
    download_url = file_info.get(b"download_url").decode()
    expiration_time = int(file_info.get(b"expiration_time").decode())  # Преобразуем в int
    start_file_name = file_info.get(b"start_file_name").decode()

    # Передаем expiration_time как timestamp
    return templates.TemplateResponse(
        "file_info.html",
        {
            "request": request,
            "file_id": file_id,
            "file_path": file_path,
            "download_url": download_url,
            "expiration_time": expiration_time,  # Передаем как timestamp
            "start_file_name": start_file_name,
        }
    )
