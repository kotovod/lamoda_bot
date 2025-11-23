# 🚀 ПЕРЕНОС БОТА НА СЕРВЕР - Пошаговая инструкция

## 📋 Что понадобится:

- VPS/сервер с Ubuntu/Debian (или любой Linux)
- SSH доступ к серверу
- Python 3.8+ на сервере
- 5-10 минут времени

---

## 🎯 ВАРИАНТ 1: Через Git (РЕКОМЕНДУЕТСЯ)

### Шаг 1: Подключитесь к серверу

```bash
ssh ваш_пользователь@IP_сервера

# Например:
# ssh ubuntu@192.168.1.100
# или
# ssh root@your-server.com
```

### Шаг 2: Установите необходимые пакеты

```bash
# Обновляем систему
sudo apt update

# Устанавливаем Python и git
sudo apt install -y python3 python3-pip python3-venv git

# Проверяем версию Python (должно быть 3.8+)
python3 --version
```

### Шаг 3: Клонируйте репозиторий

```bash
# Перейдите в домашнюю директорию
cd ~

# Клонируйте репозиторий (замените на ваш URL)
git clone https://github.com/ваш_username/Lamoda_bot.git

# ИЛИ если репозиторий приватный:
git clone https://ваш_токен@github.com/ваш_username/Lamoda_bot.git

# Перейдите в папку проекта
cd Lamoda_bot
```

### Шаг 4: Установите зависимости

```bash
# Создайте виртуальное окружение
python3 -m venv venv

# Активируйте его
source venv/bin/activate

# Установите пакеты
pip install -r requirements.txt

# Проверка установки
pip list
```

### Шаг 5: Проверьте что бот работает (тест)

```bash
# Запустите тест
python test_bot.py

# Должно показать:
# ✅ Получено товаров: XX
# ✅ Chat ID: XXXXXX
```

Если все ОК - продолжаем!

### Шаг 6: Настройте systemd (автозапуск)

```bash
# Откройте конфигурацию service
nano lamoda-monitor.service

# Замените YOUR_USERNAME на ваш username сервера
# Узнать username: whoami
# Например если у вас ubuntu, замените:
# User=ubuntu
# WorkingDirectory=/home/ubuntu/Lamoda_bot
# ExecStart=/home/ubuntu/Lamoda_bot/venv/bin/python ...

# Сохраните: Ctrl+O, Enter, Ctrl+X
```

### Шаг 7: Установите service

```bash
# Скопируйте service файл
sudo cp lamoda-monitor.service /etc/systemd/system/

# Перезагрузите systemd
sudo systemctl daemon-reload

# Включите автозапуск при старте системы
sudo systemctl enable lamoda-monitor

# Запустите бота
sudo systemctl start lamoda-monitor

# Проверьте статус
sudo systemctl status lamoda-monitor
```

Должно показать: **Active: active (running)**

### Шаг 8: Проверьте логи

```bash
# Смотрим логи в реальном времени
sudo journalctl -u lamoda-monitor -f

# ИЛИ смотрим файл логов
tail -f ~/Lamoda_bot/lamoda_monitor.log

# Должно быть:
# "🚀 Запуск Lamoda Monitor Bot"
# "✅ Chat ID: XXXXXX"
# "🔍 Проверка новых товаров..."
```

### ✅ ГОТОВО! Бот работает на сервере 24/7!

---

## 🎯 ВАРИАНТ 2: Через SCP (загрузка файлов)

Если нет Git или не хотите создавать репозиторий:

### На вашем компьютере:

```bash
# Архивируем папку проекта
cd ~/Desktop
tar -czf Lamoda_bot.tar.gz Lamoda_bot/

# Загружаем на сервер
scp Lamoda_bot.tar.gz ваш_user@IP_сервера:~

# Например:
# scp Lamoda_bot.tar.gz ubuntu@192.168.1.100:~
```

### На сервере:

```bash
# Подключаемся
ssh ваш_user@IP_сервера

# Распаковываем
cd ~
tar -xzf Lamoda_bot.tar.gz
cd Lamoda_bot

# Дальше следуем инструкциям из Варианта 1 начиная с Шага 4
```

---

## 🛠️ УПРАВЛЕНИЕ БОТОМ НА СЕРВЕРЕ

### Основные команды:

```bash
# Посмотреть статус
sudo systemctl status lamoda-monitor

# Остановить бота
sudo systemctl stop lamoda-monitor

# Запустить бота
sudo systemctl start lamoda-monitor

# Перезапустить бота
sudo systemctl restart lamoda-monitor

# Посмотреть логи
sudo journalctl -u lamoda-monitor -f

# ИЛИ
tail -f ~/Lamoda_bot/lamoda_monitor.log

# Отключить автозапуск
sudo systemctl disable lamoda-monitor
```

### Если нужно обновить код:

```bash
cd ~/Lamoda_bot
git pull
sudo systemctl restart lamoda-monitor
```

---

## 🔧 ИЗМЕНЕНИЕ НАСТРОЕК

### Изменить интервал проверки:

```bash
cd ~/Lamoda_bot
nano lamoda_monitor_bot.py

# Найдите строку:
# CHECK_INTERVAL = 3600  # 1 час

# Измените на нужное (в секундах):
# CHECK_INTERVAL = 1800  # 30 минут
# CHECK_INTERVAL = 600   # 10 минут

# Сохраните и перезапустите:
sudo systemctl restart lamoda-monitor
```

### Очистить базу известных товаров:

```bash
cd ~/Lamoda_bot
rm known_products.json
sudo systemctl restart lamoda-monitor

# Бот заново загрузит все товары
```

---

## 📊 МОНИТОРИНГ РАБОТЫ БОТА

### Проверить что бот живой:

```bash
# Должно показать "active (running)"
sudo systemctl status lamoda-monitor
```

### Посмотреть последние проверки:

```bash
# Последние 50 строк лога
tail -n 50 ~/Lamoda_bot/lamoda_monitor.log

# В реальном времени
tail -f ~/Lamoda_bot/lamoda_monitor.log
```

### Сколько товаров в базе:

```bash
cd ~/Lamoda_bot
cat known_products.json | jq '. | length'

# Если нет jq:
sudo apt install jq
```

---

## ❗ ВАЖНЫЕ МОМЕНТЫ

### 1. Firewall
Если у вас включен firewall, проверьте что разрешен исходящий трафик (для Telegram API).

### 2. Часовой пояс
Проверьте часовой пояс сервера:
```bash
timedatectl

# Если нужно изменить:
sudo timedatectl set-timezone Europe/Moscow
```

### 3. Автоматический перезапуск
Service настроен на автоматический перезапуск при падении:
```
Restart=always
RestartSec=10
```

### 4. Логи ротация
Чтобы логи не заполнили диск, настройте logrotate:
```bash
sudo nano /etc/logrotate.d/lamoda-monitor

# Добавьте:
/home/YOUR_USERNAME/Lamoda_bot/lamoda_monitor.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

---

## 🆘 РЕШЕНИЕ ПРОБЛЕМ

### Бот не запускается:

```bash
# Смотрим подробные логи
sudo journalctl -u lamoda-monitor -n 100 --no-pager

# Проверяем права
ls -la ~/Lamoda_bot/lamoda_monitor_bot.py

# Проверяем Python
~/Lamoda_bot/venv/bin/python --version
```

### Не приходят уведомления:

```bash
# Проверяем интернет
ping -c 3 api.telegram.org

# Проверяем токен бота
curl https://api.telegram.org/bot7926186760:AAFQ-N4S55QRh4nI0WwPxU2p4cQ1PKTLFiU/getMe

# Проверяем Chat ID
cat ~/Lamoda_bot/chat_id.json
```

### Бот падает:

```bash
# Смотрим последние ошибки
sudo journalctl -u lamoda-monitor -n 50 | grep ERROR

# Перезапускаем
sudo systemctl restart lamoda-monitor
```

---

## ✅ ПРОВЕРОЧНЫЙ ЧЕКЛИСТ

После установки проверьте:

- [ ] `sudo systemctl status lamoda-monitor` показывает **active (running)**
- [ ] В Telegram пришло сообщение "🤖 Lamoda Monitor Bot запущен!"
- [ ] В логах нет ошибок: `tail ~/Lamoda_bot/lamoda_monitor.log`
- [ ] Файл `known_products.json` создан и содержит SKU товаров
- [ ] Бот переживает перезагрузку сервера: `sudo reboot`

---

## 🎉 ГОТОВО!

Ваш бот работает на сервере 24/7! 

Он будет:
- ⏰ Проверять каждый час
- 🆕 Находить новые товары
- 📱 Присылать уведомления в Telegram
- 🔄 Автоматически перезапускаться при падении
- 🚀 Запускаться при старте сервера

**Следующая проверка через час!** ⏰

