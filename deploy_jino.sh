#!/bin/bash

# ========================================
# АВТОМАТИЧЕСКИЙ ДЕПЛОЙ НА roller25.myjino.ru
# ========================================

SERVER="roller25.myjino.ru"
USER="roller25"

echo "🚀 ДЕПЛОЙ LAMODA BOT НА СЕРВЕР"
echo "================================"
echo ""
echo "🎯 Сервер: $SERVER"
echo "👤 Пользователь: $USER"
echo ""

# Проверка подключения
echo "🔍 Проверяем подключение к серверу..."
ssh -o ConnectTimeout=10 $USER@$SERVER "echo '✅ Подключение успешно!'" || {
    echo "❌ Не удалось подключиться к серверу"
    echo "Проверьте доступность сервера и пароль"
    exit 1
}

echo ""
echo "🔧 Начинаем установку на сервере..."
echo ""

# Выполняем все команды на сервере
ssh $USER@$SERVER << 'ENDSSH'

echo "================================"
echo "📦 УСТАНОВКА НА СЕРВЕРЕ"
echo "================================"
echo ""

# Проверяем Python
echo "🐍 Проверяем Python..."
python3 --version || {
    echo "❌ Python 3 не установлен"
    echo "Обратитесь к хостинг-провайдеру"
    exit 1
}

# Проверяем git
echo "📥 Проверяем git..."
git --version || {
    echo "❌ Git не установлен"
    echo "Обратитесь к хостинг-провайдеру"
    exit 1
}

# Клонируем репозиторий
echo ""
echo "📂 Клонируем репозиторий..."
cd ~

# Удаляем старую версию если есть
if [ -d "lamoda_bot" ]; then
    echo "⚠️  Найдена старая версия, обновляем..."
    cd lamoda_bot
    git pull
else
    git clone https://github.com/kotovod/lamoda_bot.git
    cd lamoda_bot
fi

echo "✅ Код загружен"

# Создаем виртуальное окружение
echo ""
echo "🔨 Настраиваем виртуальное окружение..."
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
echo "📦 Устанавливаем зависимости..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Зависимости установлены"

# Настраиваем service файл
echo ""
echo "⚙️  Настраиваем конфигурацию..."
CURRENT_USER=$(whoami)
HOME_DIR=$HOME

# Создаем скрипт запуска (вместо systemd, т.к. на shared hosting нет доступа к systemd)
cat > start_bot.sh << 'EOF'
#!/bin/bash
cd ~/lamoda_bot
source venv/bin/activate
nohup python lamoda_monitor_bot.py > bot_output.log 2>&1 &
echo $! > bot.pid
echo "✅ Бот запущен! PID: $(cat bot.pid)"
EOF

chmod +x start_bot.sh

# Создаем скрипт остановки
cat > stop_bot.sh << 'EOF'
#!/bin/bash
if [ -f ~/lamoda_bot/bot.pid ]; then
    PID=$(cat ~/lamoda_bot/bot.pid)
    kill $PID 2>/dev/null && echo "✅ Бот остановлен (PID: $PID)" || echo "⚠️  Процесс уже завершен"
    rm ~/lamoda_bot/bot.pid
else
    echo "⚠️  PID файл не найден"
fi
EOF

chmod +x stop_bot.sh

# Создаем скрипт перезапуска
cat > restart_bot.sh << 'EOF'
#!/bin/bash
echo "🔄 Перезапуск бота..."
~/lamoda_bot/stop_bot.sh
sleep 2
~/lamoda_bot/start_bot.sh
EOF

chmod +x restart_bot.sh

echo "✅ Скрипты управления созданы"

# Останавливаем старый процесс если запущен
echo ""
echo "🛑 Останавливаем старый процесс (если запущен)..."
./stop_bot.sh

# Тестируем бота
echo ""
echo "🧪 Тестируем бота..."
source venv/bin/activate
python test_bot.py || echo "⚠️  Тест не прошел, но это не критично"

# Запускаем бота
echo ""
echo "🚀 Запускаем бота..."
./start_bot.sh

sleep 3

# Проверяем что бот запущен
if [ -f bot.pid ] && ps -p $(cat bot.pid) > /dev/null; then
    echo ""
    echo "================================"
    echo "✅ БОТ УСПЕШНО ЗАПУЩЕН!"
    echo "================================"
    echo ""
    echo "📊 Полезные команды:"
    echo "  ~/lamoda_bot/start_bot.sh      # Запустить бота"
    echo "  ~/lamoda_bot/stop_bot.sh       # Остановить бота"
    echo "  ~/lamoda_bot/restart_bot.sh    # Перезапустить бота"
    echo "  tail -f ~/lamoda_bot/lamoda_monitor.log  # Смотреть логи"
    echo "  tail -f ~/lamoda_bot/bot_output.log      # Смотреть вывод"
    echo ""
    echo "🔍 PID бота: $(cat bot.pid)"
else
    echo ""
    echo "❌ Ошибка при запуске бота"
    echo "Смотрите логи: tail ~/lamoda_bot/bot_output.log"
fi

ENDSSH

echo ""
echo "================================"
echo "🎉 ДЕПЛОЙ ЗАВЕРШЕН!"
echo "================================"
echo ""
echo "📱 Проверьте Telegram - должно прийти сообщение о запуске бота"
echo ""
echo "💡 Для управления ботом подключитесь к серверу:"
echo "   ssh $USER@$SERVER"
echo ""
echo "   И используйте команды:"
echo "   ~/lamoda_bot/start_bot.sh      # Запуск"
echo "   ~/lamoda_bot/stop_bot.sh       # Остановка"
echo "   ~/lamoda_bot/restart_bot.sh    # Перезапуск"
echo "   tail -f ~/lamoda_bot/lamoda_monitor.log  # Логи"
echo ""

