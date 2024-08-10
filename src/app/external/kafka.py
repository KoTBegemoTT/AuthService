
import asyncio

import aiofiles
import brotli
from aiokafka import AIOKafkaProducer
from fastapi import HTTPException, UploadFile, status

from app.config import settings

loop = asyncio.get_event_loop()
producer = AIOKafkaProducer(
    loop=loop, bootstrap_servers=settings.kafka_instance,
)


async def compress(message: str) -> bytes:
    """Сжатие файла."""
    return brotli.compress(
        bytes(message, settings.file_encoding),
        quality=settings.file_compression_quality,
    )


async def verify_view(user_photo: UploadFile, user_id: int) -> dict:
    """Подтверждение пользователя."""
    file_path = f'/usr/photos/{user_photo.filename}'

    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            file_content = await user_photo.read()
            await out_file.write(file_content)

            compressed_path = await compress(file_path)
            await producer.send_and_wait(
                settings.kafka_producer_topic, compressed_path, user_id,
            )
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex),
        )

    return {'message': 'File saved successfully'}
