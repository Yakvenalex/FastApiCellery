import os
import datetime
from fastapi import APIRouter, UploadFile, HTTPException, Form
from loguru import logger
from app.api.utils import generate_random_string, get_file_data
from app.config import settings, celery_app, redis_client

router = APIRouter(tags=['API'])


@router.post("/api/upload/")
async def upload_file(file: UploadFile, expiration_minutes: int = Form(...)):
    try:

        # Read the uploaded file
        file_content = await file.read()
        start_file_name = file.filename
        # Generate unique file name and deletion ID
        file_extension = os.path.splitext(file.filename)[1]
        file_id = generate_random_string(12)
        dell_id = generate_random_string(12)

        # Save the file to disk
        file_path = os.path.join(settings.UPLOAD_DIR, file_id + file_extension)
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Calculate expiration time in seconds
        expiration_seconds = expiration_minutes * 60
        expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=expiration_seconds)

        # Schedule the task to delete the file after expiration time
        celery_app.send_task('delete_file_scheduled', args=[file_id, dell_id], countdown=expiration_seconds)

        # Metadata URLs
        download_url = f"{settings.BASE_URL}/files/{file_id + file_extension}"
        view_url = f"{settings.BASE_URL}/view_file/{file_id}"

        # Save metadata to Redis
        redis_key = f"file:{file_id}"  # Unique key for the file
        redis_client.hmset(redis_key, {"file_path": file_path,
                                       "dell_id": dell_id,
                                       "download_url": download_url,
                                       "expiration_time": int(expiration_time.timestamp()),
                                       "start_file_name": start_file_name})

        return {
            "message": "File uploaded successfully",
            "file_id": file_id,
            "dell_id": dell_id,
            "download_url": download_url,
            "view_url": view_url,
            "expiration_time": expiration_time.isoformat(),
            "expiration_seconds": expiration_seconds
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@router.delete("/delete/{file_id}/{dell_id}")
async def delete_file(file_id: str, dell_id: str):
    redis_key = f"file:{file_id}"
    file_info = redis_client.hgetall(redis_key)

    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")

    dell_id_redis = file_info.get(b"dell_id").decode()
    if dell_id_redis != dell_id:
        raise HTTPException(status_code=403, detail="Invalid deletion ID")

    file_path = file_info.get(b"file_path").decode()

    # Удаление файла и очистка записи в Redis
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Файл {file_path} успешно удален!")
        else:
            logger.warning(f"Файл {file_path} не найден.")

        redis_client.delete(redis_key)
        return {"message": "Файл успешно удален и запись в Redis очищена!"}

    except OSError as e:
        logger.error(f"Error deleting file {file_path}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")


