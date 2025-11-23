# 🤖 LAMODA MONITOR BOT - Инструкция по установке

## 📋 Что делает бот

Автоматически отслеживает появление новых товаров Adidas Originals на Lamoda и присылает уведомления в Telegram:
- 📦 Название товара
- 💰 Цена
- 🖼️ Фото товара
- 🔗 Ссылка на товар

**Частота проверки:** каждый час

---

## 🚀 БЫСТРАЯ УСТАНОВКА НА СЕРВЕРЕ

### Шаг 1: Подключитесь к серверу

```bash
ssh your_user@your_server_ip
```

### Шаг 2: Загрузите проект

```bash
# Склонируйте репозиторий или загрузите файлы
git clone YOUR_REPO_URL Lamoda_bot
cd Lamoda_bot

# Или создайте директорию и загрузите файлы вручную
mkdir -p ~/Lamoda_bot
cd ~/Lamoda_bot
```

### Шаг 3: Установите зависимости

```bash
# Создайте виртуальное окружение
python3 -m venv venv

# Активируйте
source venv/bin/activate

# Установите пакеты
pip install -r requirements.txt
```

### Шаг 4: Получите Chat ID

**ВАЖНО:** Перед запуском отправьте любое сообщение вашему боту в Telegram!

```bash
# Найдите ваш Chat ID
curl https://api.telegram.org/bot7926186760:AAFQ-N4S55QRh4nI0WwPxU2p4cQ1PKTLFiU/getUpdates
```

В ответе найдите: `"chat":{"id":123456789,...}` - это ваш Chat ID

### Шаг 5: Настройте systemd service

```bash
# Откройте файл конфигурации
nano lamoda-monitor.service

# Замените YOUR_USERNAME на ваше имя пользователя (обычно это ваш логин)
# Например, если путь /home/ubuntu/Lamoda_bot, то YOUR_USERNAME = ubuntu

# Скопируйте service в systemd
sudo cp lamoda-monitor.service /etc/systemd/system/

# Перезагрузите systemd
sudo systemctl daemon-reload

# Включите автозапуск
sudo systemctl enable lamoda-monitor

# Запустите бота
sudo systemctl start lamoda-monitor
```

### Шаг 6: Проверьте работу

```bash
# Статус бота
sudo systemctl status lamoda-monitor

# Логи в реальном времени
sudo journalctl -u lamoda-monitor -f

# Или смотрите файл логов
tail -f ~/Lamoda_bot/lamoda_monitor.log
```

---

## ✅ ПРОВЕРКА РАБОТЫ

После запуска бот должен:
1. ✅ Прислать в Telegram: "🤖 Lamoda Monitor Bot запущен!"
2. ✅ Начать проверку каждый час
3. ✅ Присылать уведомления о новых товарах

---

## 🛠️ УПРАВЛЕНИЕ БОТОМ

```bash
# Остановить бота
sudo systemctl stop lamoda-monitor

# Запустить бота
sudo systemctl start lamoda-monitor

# Перезапустить бота
sudo systemctl restart lamoda-monitor

# Посмотреть статус
sudo systemctl status lamoda-monitor

# Отключить автозапуск
sudo systemctl disable lamoda-monitor

# Логи
tail -f ~/Lamoda_bot/lamoda_monitor.log
```

---

## 📝 ТЕСТИРОВАНИЕ (локально перед деплоем)

```bash
cd /Users/kotovod/Desktop/Lamoda_bot
source venv/bin/activate

# Запустите бота
python lamoda_monitor_bot.py
```

**Что произойдет:**
1. Бот запустится и пришлет приветственное сообщение
2. Загрузит текущие товары в базу (первый запуск)
3. Начнет проверку каждый час
4. При появлении нового товара - пришлет уведомление

**Для остановки:** Ctrl+C

---

## 🔧 НАСТРОЙКА

Все настройки в файле `lamoda_monitor_bot.py`:

```python
# Токен бота
TELEGRAM_BOT_TOKEN = "7926186760:AAFQ-N4S55QRh4nI0WwPxU2p4cQ1PKTLFiU"

# URL категории
LAMODA_URL = "https://www.lamoda.ru/b/1163/brand-adidasoriginals/?sort=new"

# Интервал проверки (секунды)
CHECK_INTERVAL = 3600  # 1 час
```

---

## 📂 ФАЙЛЫ ПРОЕКТА

После запуска будут созданы:

- `known_products.json` - база известных товаров
- `chat_id.json` - сохраненный Chat ID
- `lamoda_monitor.log` - логи работы бота

---

## ❓ ЧАСТЫЕ ВОПРОСЫ

### Как изменить интервал проверки?

В файле `lamoda_monitor_bot.py`:
```python
CHECK_INTERVAL = 1800  # 30 минут
CHECK_INTERVAL = 600   # 10 минут
```

### Как добавить другую категорию?

Измените `LAMODA_URL` на нужную категорию.

### Как очистить базу известных товаров?

```bash
rm known_products.json
sudo systemctl restart lamoda-monitor
```

### Бот не присылает уведомления?

1. Проверьте логи: `tail -f lamoda_monitor.log`
2. Убедитесь, что отправили сообщение боту
3. Проверьте Chat ID
4. Проверьте интернет на сервере

---

## 🎯 ПЕРВЫЙ ЗАПУСК - ЧТО ПРОИЗОЙДЕТ

1. **Инициализация базы:** Бот загрузит текущие ~60 товаров и сохранит их как "известные"
2. **Проверка раз в час:** Через час проверит снова
3. **Уведомления:** Если появятся новые товары - пришлет сообщения

**ВАЖНО:** При первом запуске уведомлений не будет (загружается база). Уведомления начнутся со второй проверки.

---

## 🆘 ПОДДЕРЖКА

Если что-то не работает:

1. Проверьте логи: `tail -f ~/Lamoda_bot/lamoda_monitor.log`
2. Проверьте статус: `sudo systemctl status lamoda-monitor`
3. Проверьте интернет: `ping google.com`
4. Убедитесь, что Chat ID правильный

---

## ✨ ГОТОВО!

Бот будет работать 24/7 и присылать уведомления о новых товарах Adidas Originals! 🎉

