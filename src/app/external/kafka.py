
import aiofiles
from aiokafka import AIOKafkaProducer
import brotli
from fastapi import HTTPException, UploadFile
from app.config import settings

producer = AIOKafkaProducer(bootstrap_servers=settings.kafka_instance)


async def compress(message: str) -> bytes:
    return brotli.compress(
        bytes(message, settings.file_encoding),
        quality=1,
    )


async def verify_view(file: UploadFile) -> dict:
    file_path = f"/usr/photos/{file.filename}"

    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

            compressed_path = await compress(file_path)
            await producer.send_and_wait(
                settings.kafka_producer_topic, compressed_path
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "File saved successfully"}


# async def verify_view(file: UploadFile) -> dict:
#     try:
#         file_path = f"/usr/photos/{file.filename}"
#         with open(file_path, "wb") as f:
#             f.write(file.file.read())
#             await producer.send_and_wait(
#                 settings.kafka_producer_topic, await compress(file_path)
#             )
#             return {"message": "File saved successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
