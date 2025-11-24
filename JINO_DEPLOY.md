# 🚀 ДЕПЛОЙ НА JINO.RU - Инструкция

## ✅ Ваши данные:

- **Сервер:** roller25.myjino.ru
- **Логин:** roller25
- **Пароль:** IG59ar8089@ssh

---

## 🎯 АВТОМАТИЧЕСКИЙ ДЕПЛОЙ (РЕКОМЕНДУЕТСЯ)

### Запустите скрипт:

```bash
cd /Users/kotovod/Desktop/Lamoda_bot
./deploy_jino.sh
```

Скрипт попросит **пароль** и автоматически:
- ✅ Подключится к серверу
- ✅ Клонирует код из GitHub
- ✅ Установит зависимости
- ✅ Создаст скрипты управления
- ✅ Запустит бота

**Готово!** Бот будет работать на сервере! 🎉

---

## 📋 РУЧНОЙ ДЕПЛОЙ (пошагово)

### Шаг 1: Подключитесь к серверу

```bash
ssh roller25@roller25.myjino.ru
# Введите пароль: IG59ar8089@ssh
```

### Шаг 2: Клонируйте репозиторий

```bash
cd ~
git clone https://github.com/kotovod/lamoda_bot.git
cd lamoda_bot
```

### Шаг 3: Установите зависимости

```bash
# Проверьте Python
python3 --version

# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установите пакеты
pip install --upgrade pip
pip install -r requirements.txt
```

### Шаг 4: Создайте скрипты управления

**⚠️ ВАЖНО:** На shared хостинге (Jino) нет доступа к systemd, поэтому используем обычные скрипты.

#### Создайте `start_bot.sh`:

```bash
cat > ~/lamoda_bot/start_bot.sh << 'EOF'
#!/bin/bash
cd ~/lamoda_bot
source venv/bin/activate
nohup python lamoda_monitor_bot.py > bot_output.log 2>&1 &
echo $! > bot.pid
echo "✅ Бот запущен! PID: $(cat bot.pid)"
EOF

chmod +x ~/lamoda_bot/start_bot.sh
```

#### Создайте `stop_bot.sh`:

```bash
cat > ~/lamoda_bot/stop_bot.sh << 'EOF'
#!/bin/bash
if [ -f ~/lamoda_bot/bot.pid ]; then
    PID=$(cat ~/lamoda_bot/bot.pid)
    kill $PID 2>/dev/null && echo "✅ Бот остановлен" || echo "⚠️  Процесс уже завершен"
    rm ~/lamoda_bot/bot.pid
else
    echo "⚠️  PID файл не найден"
fi
EOF

chmod +x ~/lamoda_bot/stop_bot.sh
```

#### Создайте `restart_bot.sh`:

```bash
cat > ~/lamoda_bot/restart_bot.sh << 'EOF'
#!/bin/bash
~/lamoda_bot/stop_bot.sh
sleep 2
~/lamoda_bot/start_bot.sh
EOF

chmod +x ~/lamoda_bot/restart_bot.sh
```

### Шаг 5: Запустите бота

```bash
cd ~/lamoda_bot
./start_bot.sh
```

### Шаг 6: Проверьте

```bash
# Проверьте что процесс запущен
ps aux | grep lamoda_monitor_bot.py

# Смотрите логи
tail -f ~/lamoda_bot/lamoda_monitor.log
```

✅ **Готово!** Бот работает!

---

## 🛠️ УПРАВЛЕНИЕ БОТОМ

### Основные команды:

```bash
# Подключитесь к серверу
ssh roller25@roller25.myjino.ru

# Запустить бота
~/lamoda_bot/start_bot.sh

# Остановить бота
~/lamoda_bot/stop_bot.sh

# Перезапустить бота
~/lamoda_bot/restart_bot.sh

# Посмотреть логи
tail -f ~/lamoda_bot/lamoda_monitor.log

# Посмотреть вывод бота
tail -f ~/lamoda_bot/bot_output.log

# Проверить что бот запущен
ps aux | grep lamoda_monitor_bot.py
```

---

## 🔄 АВТОЗАПУСК ПОСЛЕ ПЕРЕЗАГРУЗКИ

На Jino нет systemd, поэтому нужно использовать **cron**:

```bash
# Откройте crontab
crontab -e

# Добавьте строку (запуск при загрузке):
@reboot sleep 60 && ~/lamoda_bot/start_bot.sh

# Сохраните: Ctrl+O, Enter, Ctrl+X (если nano)
```

---

## 📊 МОНИТОРИНГ

### Проверка что бот работает:

```bash
# Процесс запущен?
ps aux | grep python | grep lamoda

# Последние строки лога
tail -n 20 ~/lamoda_bot/lamoda_monitor.log

# Логи в реальном времени
tail -f ~/lamoda_bot/lamoda_monitor.log
```

### Количество известных товаров:

```bash
wc -l ~/lamoda_bot/known_products.json
```

---

## 🆘 РЕШЕНИЕ ПРОБЛЕМ

### Бот не запускается:

```bash
# Смотрим вывод
cat ~/lamoda_bot/bot_output.log

# Тестируем вручную
cd ~/lamoda_bot
source venv/bin/activate
python test_bot.py
```

### Бот не присылает уведомления:

```bash
# Проверяем Chat ID
cat ~/lamoda_bot/chat_id.json

# Проверяем логи
tail -f ~/lamoda_bot/lamoda_monitor.log
```

### Нужно обновить код:

```bash
ssh roller25@roller25.myjino.ru
cd ~/lamoda_bot
git pull
~/lamoda_bot/restart_bot.sh
```

### Очистить базу товаров:

```bash
ssh roller25@roller25.myjino.ru
cd ~/lamoda_bot
rm known_products.json
~/lamoda_bot/restart_bot.sh
```

---

## ⚡ БЫСТРЫЕ КОМАНДЫ

Скопируйте и вставьте:

### Первая установка:

```bash
ssh roller25@roller25.myjino.ru
cd ~ && git clone https://github.com/kotovod/lamoda_bot.git && cd lamoda_bot
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cat > start_bot.sh << 'EOF'
#!/bin/bash
cd ~/lamoda_bot && source venv/bin/activate
nohup python lamoda_monitor_bot.py > bot_output.log 2>&1 &
echo $! > bot.pid && echo "✅ Бот запущен! PID: $(cat bot.pid)"
EOF
chmod +x start_bot.sh && ./start_bot.sh
```

### Быстрая проверка:

```bash
ssh roller25@roller25.myjino.ru "ps aux | grep lamoda && tail -n 10 ~/lamoda_bot/lamoda_monitor.log"
```

---

## ✅ ПРОВЕРОЧНЫЙ ЧЕКЛИСТ

После установки:

- [ ] Бот запущен: `ps aux | grep lamoda`
- [ ] В Telegram пришло: "🤖 Lamoda Monitor Bot запущен!"
- [ ] Логи без ошибок: `tail ~/lamoda_bot/lamoda_monitor.log`
- [ ] Файл `bot.pid` создан: `cat ~/lamoda_bot/bot.pid`
- [ ] Процесс работает: `kill -0 $(cat ~/lamoda_bot/bot.pid)`

---

## 🎉 ГОТОВО!

Ваш бот работает на сервере Jino!

- ⏰ Проверяет каждый час
- 🆕 Находит новые товары
- 📱 Присылает в Telegram
- 🔄 Автоматически перезапускается (если настроили cron)

**Следующая проверка через час!** ⏰

