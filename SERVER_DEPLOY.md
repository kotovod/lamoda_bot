# 🚀 ДЕПЛОЙ НА СЕРВЕР - Пошаговая инструкция

## 📋 Что нужно для деплоя

1. ✅ Сервер (VPS) с Ubuntu/Debian/CentOS
2. ✅ SSH доступ к серверу
3. ✅ Python 3.7+ (обычно уже установлен)
4. ✅ Бот протестирован локально (работает!)

---

## 🎯 ВАРИАНТ 1: Автоматический деплой (рекомендуется)

### Шаг 1: Подключитесь к серверу

```bash
ssh your_username@your_server_ip
```

### Шаг 2: Загрузите проект на сервер

**Способ А - Через Git (если репозиторий на GitHub):**

```bash
git clone https://github.com/YOUR_USERNAME/Lamoda_bot.git
cd Lamoda_bot
```

**Способ Б - Через scp с вашего компьютера:**

На вашем компьютере (macOS) выполните:

```bash
# Архивируем проект
cd /Users/kotovod/Desktop
tar -czf lamoda_bot.tar.gz Lamoda_bot/

# Копируем на сервер
scp lamoda_bot.tar.gz your_username@your_server_ip:~/

# На сервере распакуйте:
ssh your_username@your_server_ip
cd ~
tar -xzf lamoda_bot.tar.gz
cd Lamoda_bot
```

### Шаг 3: Запустите автоматический деплой

```bash
chmod +x deploy.sh
./deploy.sh
```

Скрипт автоматически:
- ✅ Создаст виртуальное окружение
- ✅ Установит зависимости
- ✅ Настроит systemd service
- ✅ Запустит бота

### Шаг 4: Проверьте работу

```bash
# Статус бота
sudo systemctl status lamoda-monitor

# Логи в реальном времени
tail -f ~/Lamoda_bot/lamoda_monitor.log
```

**Готово! Бот работает 24/7!** 🎉

---

## 🎯 ВАРИАНТ 2: Ручная установка

Если автоскрипт не подходит, вот пошаговая инструкция:

### 1. Подключитесь к серверу

```bash
ssh your_username@your_server_ip
```

### 2. Установите необходимые пакеты

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

# CentOS/RHEL
sudo yum install -y python3 python3-pip git
```

### 3. Загрузите проект

```bash
cd ~
git clone YOUR_REPO_URL Lamoda_bot
# или загрузите файлы через scp

cd Lamoda_bot
```

### 4. Создайте виртуальное окружение

```bash
python3 -m venv venv
source venv/bin/activate
```

### 5. Установите зависимости

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Настройте systemd service

Откройте файл service:
```bash
nano lamoda-monitor.service
```

Замените `YOUR_USERNAME` на ваше имя пользователя:
```bash
# Узнать ваше имя пользователя:
whoami
```

Скопируйте service в systemd:
```bash
sudo cp lamoda-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
```

### 7. Запустите бота

```bash
# Включить автозапуск
sudo systemctl enable lamoda-monitor

# Запустить
sudo systemctl start lamoda-monitor

# Проверить статус
sudo systemctl status lamoda-monitor
```

---

## 📱 ПРОВЕРКА РАБОТЫ

После запуска бот должен:

1. ✅ Прислать в Telegram: "🤖 Lamoda Monitor Bot запущен!"
2. ✅ Загрузить текущие товары в базу
3. ✅ Начать проверку каждый час

**Проверьте логи:**
```bash
tail -f ~/Lamoda_bot/lamoda_monitor.log
```

Вы увидите:
```
2025-11-23 22:00:00 - INFO - 🚀 Запуск Lamoda Monitor Bot
2025-11-23 22:00:00 - INFO - ✅ Chat ID: 123456789
2025-11-23 22:00:05 - INFO - 📊 Известных товаров: 0
2025-11-23 22:00:10 - INFO - 📦 Получено товаров: 35
2025-11-23 22:00:10 - INFO - ✅ Добавлено 35 товаров в базу
2025-11-23 22:00:10 - INFO - 💤 Следующая проверка через 60 минут
```

---

## 🛠️ УПРАВЛЕНИЕ БОТОМ

```bash
# Остановить
sudo systemctl stop lamoda-monitor

# Запустить
sudo systemctl start lamoda-monitor

# Перезапустить
sudo systemctl restart lamoda-monitor

# Посмотреть статус
sudo systemctl status lamoda-monitor

# Отключить автозапуск
sudo systemctl disable lamoda-monitor

# Логи systemd
sudo journalctl -u lamoda-monitor -f

# Логи бота
tail -f ~/Lamoda_bot/lamoda_monitor.log
```

---

## 🔧 НАСТРОЙКИ

Все настройки в файле `lamoda_monitor_bot.py`:

```python
# Изменить интервал проверки
CHECK_INTERVAL = 3600  # 1 час (в секундах)
CHECK_INTERVAL = 1800  # 30 минут
CHECK_INTERVAL = 600   # 10 минут

# Изменить категорию
LAMODA_URL = "https://www.lamoda.ru/b/1163/brand-adidasoriginals/?sort=new"
```

После изменений:
```bash
sudo systemctl restart lamoda-monitor
```

---

## 📊 МОНИТОРИНГ

### Просмотр логов в реальном времени:
```bash
tail -f ~/Lamoda_bot/lamoda_monitor.log
```

### Проверка работы:
```bash
# Статус процесса
ps aux | grep lamoda_monitor_bot

# Использование ресурсов
top -p $(pgrep -f lamoda_monitor_bot)
```

### Размер базы данных:
```bash
ls -lh ~/Lamoda_bot/known_products.json
```

---

## ❓ ЧАСТЫЕ ПРОБЛЕМЫ

### Бот не запускается?

1. Проверьте логи:
```bash
sudo journalctl -u lamoda-monitor -n 50
```

2. Проверьте права:
```bash
ls -la ~/Lamoda_bot/lamoda_monitor_bot.py
chmod +x ~/Lamoda_bot/lamoda_monitor_bot.py
```

3. Проверьте Python:
```bash
~/Lamoda_bot/venv/bin/python --version
```

### Не приходят уведомления?

1. Проверьте Chat ID в логах
2. Проверьте интернет на сервере:
```bash
ping -c 3 api.telegram.org
```

3. Проверьте токен бота:
```bash
curl "https://api.telegram.org/bot7926186760:AAFQ-N4S55QRh4nI0WwPxU2p4cQ1PKTLFiU/getMe"
```

### Бот падает?

Проверьте логи ошибок:
```bash
cat ~/Lamoda_bot/bot_error.log
```

---

## 🔐 БЕЗОПАСНОСТЬ

### Рекомендации:

1. **Не коммитьте токен в публичный репозиторий!**
   - Используйте `.env` файл
   - Добавьте `.env` в `.gitignore`

2. **Настройте firewall:**
```bash
sudo ufw allow 22/tcp  # SSH
sudo ufw enable
```

3. **Регулярно обновляйте систему:**
```bash
sudo apt update && sudo apt upgrade -y
```

---

## 📦 ФАЙЛЫ НА СЕРВЕРЕ

После установки структура:

```
~/Lamoda_bot/
├── venv/                      # Виртуальное окружение
├── lamoda_monitor_bot.py      # Главный скрипт
├── requirements.txt           # Зависимости
├── lamoda-monitor.service     # Systemd service
├── known_products.json        # База известных товаров
├── chat_id.json              # Сохраненный Chat ID
├── lamoda_monitor.log        # Логи бота
├── bot_output.log            # Stdout логи
└── bot_error.log             # Stderr логи
```

---

## ✅ ЧЕКЛИСТ ПОСЛЕ ДЕПЛОЯ

- [ ] Бот запущен: `sudo systemctl status lamoda-monitor`
- [ ] Получено приветственное сообщение в Telegram
- [ ] Логи работают: `tail -f ~/Lamoda_bot/lamoda_monitor.log`
- [ ] Автозапуск включен: `sudo systemctl is-enabled lamoda-monitor`
- [ ] Бот работает после перезагрузки: `sudo reboot` (опционально)

---

## 🎉 ГОТОВО!

Ваш бот теперь работает на сервере 24/7 и будет присылать уведомления о новых товарах каждый час!

**Для обновления бота:**
```bash
cd ~/Lamoda_bot
git pull  # если используете Git
sudo systemctl restart lamoda-monitor
```

---

## 💡 ДОПОЛНИТЕЛЬНО

### Добавить мониторинг работы бота (опционально):

Создайте cron job для проверки:
```bash
crontab -e
```

Добавьте:
```
*/15 * * * * systemctl is-active lamoda-monitor || systemctl start lamoda-monitor
```

Это будет проверять каждые 15 минут и перезапускать, если бот упал.

---

Если что-то не работает - смотрите логи! 90% проблем решается через логи. 📝

