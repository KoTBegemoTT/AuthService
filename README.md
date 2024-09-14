# AuthService

Сервис для аунтификации.

Этот сервис является частью группы микросервисов, входной точкой для которых является [ApiGateway](https://github.com/KoTBegemoTT/ApiGateway)

# REST API

`POST /api/register/`

- Регистрация пользователя. В случае успеха возвращает токен.

`POST /api/auth/`

- Аунтификация пользователя. В случае успеха возвращает токен.

`GET /api/check_token/`

- Проверка токена. В случае успеха возвращает username пользователя, которому принадлежит токен.

`GET /api/healthz/ready/`

- Получение информации о состоянии сервиса.

`POST /api/verify/`

- Получение изображение от пользователя и сохранение его, а также отправка сигнала в кафку о необходимости его обработки.

## Инструкция по запуску

### Перед началом

* Установить docker

### Запуск

```bash
docker compose build
docker compose up
```

### Важные эндпоинты *

* [http://localhost:8001/docs](http://localhost:8001/docs) - Auth service

* [http://localhost:16686](http://localhost:16686) - Веб интерфейс Jaeger

## Развёртывание в kubernetes

### Порядок развёртывания

1. Transaction
2. Auth
3. Face-Verification
4. ApiGateway

### Продакшен

```bash
cd helm/lebedev-auth
helm install my-release-name .
```

### Тестирование

```bash
cd helm/lebedev-auth
helm install my-release-name --values ./values/test.yaml
```