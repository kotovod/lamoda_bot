#!/bin/bash

# ========================================
# ИСПРАВЛЕННЫЙ ДЕПЛОЙ ДЛЯ JINO
# ========================================

SERVER="roller25.myjino.ru"
USER="roller25"

echo "🚀 ДЕПЛОЙ LAMODA BOT НА СЕРВЕР (ИСПРАВЛЕННАЯ ВЕРСИЯ)"
echo "===================================================="
echo ""

# Выполняем все команды на сервере
ssh $USER@$SERVER << 'ENDSSH'

echo "================================"
echo "📦 УСТАНОВКА НА СЕРВЕРЕ"
echo "================================"
echo ""

# Переходим в домашнюю директорию
cd ~

# Удаляем старую версию если есть проблемы
echo "🧹 Очистка..."
rm -rf lamoda_bot venv

# Клонируем репозиторий (публичный, без авторизации)
echo ""
echo "📂 Клонируем репозиторий..."
git clone https://github.com/kotovod/lamoda_bot.git

if [ ! -d "lamoda_bot" ]; then
    echo "❌ Ошибка клонирования репозитория"
    echo "Убедитесь что репозиторий публичный:"
    echo "https://github.com/kotovod/lamoda_bot/settings"
    exit 1
fi

cd lamoda_bot
echo "✅ Код загружен"

# Проверяем Python
echo ""
echo "🐍 Проверяем Python..."
PYTHON_CMD=""
if command -v python3.8 &> /dev/null; then
    PYTHON_CMD="python3.8"
elif command -v python3.7 &> /dev/null; then
    PYTHON_CMD="python3.7"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "❌ Python 3 не найден"
    exit 1
fi

echo "✅ Используем: $PYTHON_CMD ($($PYTHON_CMD --version))"

# Создаем виртуальное окружение
echo ""
echo "🔨 Создаем виртуальное окружение..."
$PYTHON_CMD -m venv venv --without-pip

if [ ! -d "venv" ]; then
    echo "❌ Не удалось создать venv"
    echo "Пробуем без venv..."
    PYTHON_CMD="$PYTHON_CMD"
else
    source venv/bin/activate
    echo "✅ Виртуальное окружение создано"
fi

# Устанавливаем pip
echo ""
echo "📦 Устанавливаем pip..."
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
$PYTHON_CMD get-pip.py --user
rm get-pip.py

# Устанавливаем зависимости
echo ""
echo "📦 Устанавливаем зависимости..."
$PYTHON_CMD -m pip install --user -r requirements.txt

echo "✅ Зависимости установлены"

# Создаем скрипт запуска
echo ""
echo "⚙️  Создаем скрипты управления..."

cat > start_bot.sh << EOF
#!/bin/bash
cd ~/lamoda_bot
if [ -d "venv" ]; then
    source venv/bin/activate
fi
nohup $PYTHON_CMD lamoda_monitor_bot.py > bot_output.log 2>&1 &
echo \$! > bot.pid
echo "✅ Бот запущен! PID: \$(cat bot.pid)"
EOF

cat > stop_bot.sh << 'EOF'
#!/bin/bash
if [ -f ~/lamoda_bot/bot.pid ]; then
    PID=$(cat ~/lamoda_bot/bot.pid)
    kill $PID 2>/dev/null && echo "✅ Бот остановлен" || echo "⚠️  Процесс уже завершен"
    rm ~/lamoda_bot/bot.pid
else
    echo "⚠️  PID файл не найден"
    # Попробуем найти и убить процесс
    pkill -f lamoda_monitor_bot.py && echo "✅ Процесс остановлен" || echo "⚠️  Процесс не найден"
fi
EOF

cat > restart_bot.sh << 'EOF'
#!/bin/bash
~/lamoda_bot/stop_bot.sh
sleep 2
~/lamoda_bot/start_bot.sh
EOF

chmod +x start_bot.sh stop_bot.sh restart_bot.sh

echo "✅ Скрипты созданы"

# Останавливаем старые процессы
echo ""
echo "🛑 Останавливаем старые процессы..."
pkill -f lamoda_monitor_bot.py 2>/dev/null || echo "Старых процессов нет"

# Тестируем
echo ""
echo "🧪 Тестируем подключение..."
$PYTHON_CMD -c "import requests; print('✅ requests работает')" || echo "⚠️  Ошибка импорта requests"

# Запускаем бота
echo ""
echo "🚀 Запускаем бота..."
./start_bot.sh

sleep 3

# Проверяем
if [ -f bot.pid ]; then
    PID=$(cat bot.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo ""
        echo "================================"
        echo "✅ БОТ УСПЕШНО ЗАПУЩЕН!"
        echo "================================"
        echo ""
        echo "🔍 PID: $PID"
        echo ""
        echo "📊 Команды управления:"
        echo "  ~/lamoda_bot/start_bot.sh"
        echo "  ~/lamoda_bot/stop_bot.sh"
        echo "  ~/lamoda_bot/restart_bot.sh"
        echo "  tail -f ~/lamoda_bot/lamoda_monitor.log"
        echo "  tail -f ~/lamoda_bot/bot_output.log"
        echo ""
        echo "📝 Первые строки лога:"
        head -n 20 ~/lamoda_bot/bot_output.log
    else
        echo "❌ Процесс не запустился"
        echo ""
        echo "📝 Лог ошибок:"
        tail -n 30 ~/lamoda_bot/bot_output.log
    fi
else
    echo "❌ PID файл не создан"
fi

ENDSSH

echo ""
echo "================================"
echo "🎉 ДЕПЛОЙ ЗАВЕРШЕН!"
echo "================================"
echo ""

