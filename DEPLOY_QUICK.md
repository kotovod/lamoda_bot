# ⚡ БЫСТРЫЙ ДЕПЛОЙ - Шпаргалка

## 📦 За 5 минут на сервер

### 1. На вашем компьютере (один раз):

```bash
# Загрузите код на GitHub/GitLab
cd /Users/kotovod/Desktop/Lamoda_bot
git remote add origin https://github.com/ваш_username/Lamoda_bot.git
git push -u origin main
```

---

### 2. На сервере:

```bash
# Подключитесь
ssh ваш_user@IP_сервера

# Установите зависимости (один раз)
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git

# Клонируйте проект
cd ~
git clone https://github.com/ваш_username/Lamoda_bot.git
cd Lamoda_bot

# Установите пакеты
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Настройте service (замените YOUR_USERNAME на ваш username)
nano lamoda-monitor.service
# Измените пути, сохраните (Ctrl+O, Enter, Ctrl+X)

# Установите service
sudo cp lamoda-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable lamoda-monitor
sudo systemctl start lamoda-monitor

# Проверьте
sudo systemctl status lamoda-monitor
```

**Готово!** Бот работает 24/7! ✅

---

## 🎯 Основные команды:

```bash
# Статус
sudo systemctl status lamoda-monitor

# Логи
tail -f ~/Lamoda_bot/lamoda_monitor.log

# Перезапуск
sudo systemctl restart lamoda-monitor

# Обновление кода
cd ~/Lamoda_bot && git pull && sudo systemctl restart lamoda-monitor
```

---

## 📝 Что изменить в lamoda-monitor.service:

```bash
# Узнайте ваш username:
whoami
# Например: ubuntu

# Тогда измените в service файле:
User=ubuntu
WorkingDirectory=/home/ubuntu/Lamoda_bot
ExecStart=/home/ubuntu/Lamoda_bot/venv/bin/python /home/ubuntu/Lamoda_bot/lamoda_monitor_bot.py
StandardOutput=append:/home/ubuntu/Lamoda_bot/bot_output.log
StandardError=append:/home/ubuntu/Lamoda_bot/bot_error.log
```

---

## ✅ Проверка что все работает:

```bash
# 1. Статус должен быть "active (running)"
sudo systemctl status lamoda-monitor

# 2. В Telegram должно прийти сообщение о запуске

# 3. В логах не должно быть ошибок
tail -f ~/Lamoda_bot/lamoda_monitor.log
```

---

## 🔥 Если что-то не так:

```bash
# Смотрим ошибки
sudo journalctl -u lamoda-monitor -n 50

# Тестируем вручную
cd ~/Lamoda_bot
source venv/bin/activate
python test_bot.py
```

---

**Подробная инструкция:** См. `DEPLOY_GUIDE.md`

