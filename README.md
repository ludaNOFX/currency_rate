# Currency Rate Service

## Описание сервиса
Асинхронный сервис для отслеживания и управления валютными активами с возможностью:
- Автоматического обновления курсов валют (USD, EUR, RUB по умолчанию)
- Управления балансом валют через REST API
- Конвертации между валютами
- Логирования операций

## Технологии
- Python 3.8-3.11
- FastAPI (REST API)
- Pydantic (валидация данных)
- HTTPX (асинхронные HTTP-запросы)
- Asyncio (асинхронная работа)
- Logging (логирование)

## Запуск сервиса
!!! ПЕРЕД ЗАПУСКОМ СЕРВИСОВ УКАЖИТЕ ПЕРЕМЕННУЮ ОКРУЖЕНИЯ !!!
export PROJ_ENV=local
export PROJ_ENV=prod
export PROJ_ENV=test
### Базовый запуск (с параметрами по умолчанию):
```bash
python3 -m main --rub 1000 --usd 100 --eur 50 --period 10
```

### Параметры запуска:
| Параметр  | Описание                          | Пример           |
|-----------|-----------------------------------|------------------|
| --rub     | Начальный баланс RUB              | --rub 1000       |
| --usd     | Начальный баланс USD              | --usd 200        |
| --eur     | Начальный баланс EUR              | --eur 150        |
| --period  | Интервал обновления курсов (сек)  | --period 5       |
| --debug   | Режим отладки                     | --debug true     |

### Примеры запуска:
1. С балансом только в рублях:
   ```bash
   python3 -m main --rub 5000 --period 15
   ```

2. С включенным режимом отладки:
   ```bash
   python3 -m main --rub 1000 --usd 50 --debug true
   ```

3. С интервалом обновления 5000 секунд:
   ```bash
   python3 -m main --rub 1000 --usd 100 --eur 50 --period 5000
   ```

После запуска сервис будет доступен по адресу: `http://localhost:8000`

## REST API Endpoints
GET /api/docs - сваггер
### Получение данных:
- `GET /{currency}/get` - получить баланс валюты (USD, EUR, RUB)
- `GET /amount/get` - получить полную сводку по портфелю

### Изменение данных:
- `POST /amount/set` - установить новые значения балансов
- `POST /modify` - изменить текущие балансы (добавить/уменьшить)
