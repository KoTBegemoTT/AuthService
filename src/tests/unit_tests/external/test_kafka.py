import pytest

from app.external.kafka import compress


@pytest.mark.asyncio
async def test_compress():
    compressed = await compress('test')
    assert isinstance(compressed, bytes)
