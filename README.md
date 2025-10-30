# Pharmalia Welcome Bot (Cloud Run, aiogram webhook)

Простой Telegram‑бот для Cloud Run, который:
- Приветствует новых участников в группе
- Отправляет кнопку **«📅 Записаться»** со ссылкой на `@Pharmalia`
- Работает на вебхуке (подходит для Cloud Run)

## Переменные окружения
- `BOT_TOKEN` — токен бота от BotFather
- `WEBHOOK_BASE` — публичный URL Cloud Run сервиса, например:
  `https://pharmalia-welcome-xxxxx-uc.a.run.app`

## Локальный запуск (для теста)
```bash
pip install -r requirements.txt
export BOT_TOKEN=123456:ABC...
export WEBHOOK_BASE=http://localhost:8080
python main.py
```

## Деплой в Cloud Run (Google Cloud)
1) Создай артефакт-образ:
```bash
gcloud builds submit --tag europe-central2-docker.pkg.dev/PROJECT_ID/REPO/pharmalia-welcome-bot
```

2) Деплой:
```bash
gcloud run deploy pharmalia-welcome-bot       --image europe-central2-docker.pkg.dev/PROJECT_ID/REPO/pharmalia-welcome-bot       --region europe-central2       --platform managed       --allow-unauthenticated       --set-env-vars BOT_TOKEN=123456:ABC,WEBHOOK_BASE=PLACEHOLDER
```

3) Узнай фактический URL сервиса:
```bash
gcloud run services describe pharmalia-welcome-bot       --region=europe-central2 --format='value(status.url)'
```

4) Обнови переменную `WEBHOOK_BASE` и перезадеплой (иначе вебхук не установится на верный URL):
```bash
gcloud run deploy pharmalia-welcome-bot       --image europe-central2-docker.pkg.dev/PROJECT_ID/REPO/pharmalia-welcome-bot       --region europe-central2       --platform managed       --allow-unauthenticated       --set-env-vars BOT_TOKEN=123456:ABC,WEBHOOK_BASE=https://ВАШ_URL_ОТСЮДА
```

5) Добавь бота в группу и выключи privacy mode:
   - BotFather → Bot Settings → Group Privacy → **Turn off**

Готово!
