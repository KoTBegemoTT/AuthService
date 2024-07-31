FROM python:3.12-slim

WORKDIR /service

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    # Poetry's configuration:
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VERSION=1.8.3


RUN pip install "poetry==$POETRY_VERSION"

COPY poetry.lock pyproject.toml /service/

RUN poetry install --without dev --no-interaction --no-ansi

COPY ./src/app /service/app

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
