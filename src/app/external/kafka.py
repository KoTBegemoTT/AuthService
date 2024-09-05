import asyncio

import aiofiles
import brotli
from aiokafka import AIOKafkaProducer
from fastapi import HTTPException, UploadFile, status
from opentracing import global_tracer

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


async def verify_view(
    user_photo: UploadFile,
    user_id: int,
    photo_dir: str = '/usr/photos',
) -> dict:
    """Подтверждение пользователя."""
    with global_tracer().start_active_span('verify_view') as scope:
        scope.span.set_tag('user_id', str(user_id))
        file_path = f'{photo_dir}/{user_photo.filename}'

        try:
            async with aiofiles.open(file_path, 'wb') as out_file:
                file_content = await user_photo.read()
                await out_file.write(file_content)

                compressed_path = await compress(file_path)
                compresed_id = await compress(str(user_id))
                await producer.send_and_wait(
                    topic=settings.kafka_producer_topic,
                    key=compresed_id,
                    value=compressed_path,
                )
        except Exception as ex:
            scope.span.set_tag('error', str(ex))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(ex),
            )

        return {'message': 'File saved successfully'}
