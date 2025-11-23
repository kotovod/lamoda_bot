# ⚡ ШПАРГАЛКА - Деплой за 5 минут

## 🎯 САМЫЙ БЫСТРЫЙ СПОСОБ

### 1. С вашего компьютера отправьте файлы на сервер:

```bash
# Архивируйте проект
cd /Users/kotovod/Desktop
tar -czf lamoda_bot.tar.gz Lamoda_bot/

# Отправьте на сервер (замените на свои данные)
scp lamoda_bot.tar.gz username@your-server-ip:~/
```

### 2. На сервере выполните:

```bash
# Распакуйте
tar -xzf lamoda_bot.tar.gz
cd Lamoda_bot

# Запустите автодеплой
chmod +x deploy.sh
./deploy.sh
```

### 3. Готово! Проверьте:

```bash
# Статус
sudo systemctl status lamoda-monitor

# Логи
tail -f ~/Lamoda_bot/lamoda_monitor.log
```

✅ **Бот работает 24/7!**

---

## 📱 Проверьте Telegram

Должно прийти:
```
🤖 Lamoda Monitor Bot запущен!

📍 Категория: Adidas Originals
⏰ Проверка каждый час
🔔 Буду присылать уведомления о новых товарах
```

---

## 🛠️ Основные команды

```bash
# Перезапустить
sudo systemctl restart lamoda-monitor

# Остановить
sudo systemctl stop lamoda-monitor

# Логи
tail -f ~/Lamoda_bot/lamoda_monitor.log

# Статус
sudo systemctl status lamoda-monitor
```

---

## ❓ Не работает?

```bash
# Смотрим логи ошибок
sudo journalctl -u lamoda-monitor -n 100

# Проверяем Python
~/Lamoda_bot/venv/bin/python --version

# Проверяем интернет
ping -c 3 api.telegram.org
```

---

## 🔧 Изменить интервал проверки

Откройте файл:
```bash
nano ~/Lamoda_bot/lamoda_monitor_bot.py
```

Найдите и измените:
```python
CHECK_INTERVAL = 3600  # 1 час
CHECK_INTERVAL = 1800  # 30 минут  
CHECK_INTERVAL = 600   # 10 минут
```

Перезапустите:
```bash
sudo systemctl restart lamoda-monitor
```

---

## 📊 Что происходит внутри

1. **Каждый час** бот проверяет Lamoda
2. **Сравнивает** с базой известных товаров
3. **Находит новые** - отправляет в Telegram
4. **Обновляет базу** - добавляет новые товары

База товаров: `~/Lamoda_bot/known_products.json`

---

## 🎉 Все работает!

Ваш бот мониторит Lamoda 24/7 и присылает уведомления о новинках!

**Полная инструкция:** `SERVER_DEPLOY.md`

