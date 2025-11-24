#!/bin/bash

# ========================================
# ДЕПЛОЙ В ПРАВИЛЬНУЮ ДИРЕКТОРИЮ
# domain/bot.kotovod.ru/
# ========================================

SERVER="roller25.myjino.ru"
USER="roller25"

echo "🚀 ДЕПЛОЙ В domain/bot.kotovod.ru/"
echo "===================================="
echo ""

ssh $USER@$SERVER << 'ENDSSH'

echo "📂 Переходим в целевую директорию..."
cd ~/domain/bot.kotovod.ru

# Очищаем директорию (кроме служебных файлов)
echo "🧹 Очищаем директорию..."
rm -rf lamoda_bot *.py *.md *.txt *.sh *.service venv known_products.json chat_id.json *.log bot.pid 2>/dev/null

# Клонируем во временную папку
echo ""
echo "📥 Клонируем репозиторий..."
cd ~
rm -rf temp_lamoda 2>/dev/null
git clone https://github.com/kotovod/lamoda_bot.git temp_lamoda

if [ ! -d "temp_lamoda" ]; then
    echo "❌ Ошибка клонирования"
    echo "Убедитесь что репозиторий публичный:"
    echo "https://github.com/kotovod/lamoda_bot/settings"
    exit 1
fi

# Переносим файлы в целевую директорию
echo "📦 Переносим файлы в domain/bot.kotovod.ru/..."
cp -r temp_lamoda/* ~/domain/bot.kotovod.ru/
cp temp_lamoda/.gitignore ~/domain/bot.kotovod.ru/ 2>/dev/null

# Удаляем временную папку
rm -rf temp_lamoda

# Переходим в рабочую директорию
cd ~/domain/bot.kotovod.ru

echo "✅ Файлы перенесены"
echo ""
ls -la | head -20

# Определяем Python
echo ""
echo "🐍 Настраиваем Python..."
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
$PYTHON_CMD -m venv venv --without-pip 2>/dev/null || $PYTHON_CMD -m venv venv

if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Виртуальное окружение создано"
else
    echo "⚠️  Работаем без venv"
fi

# Устанавливаем pip
echo ""
echo "📦 Устанавливаем pip..."
curl -s https://bootstrap.pypa.io/get-pip.py -o get-pip.py
$PYTHON_CMD get-pip.py --user --quiet
rm get-pip.py

# Устанавливаем зависимости
echo ""
echo "📦 Устанавливаем зависимости..."
$PYTHON_CMD -m pip install --user -r requirements.txt --quiet

echo "✅ Зависимости установлены"

# Создаем скрипты управления
echo ""
echo "⚙️  Создаем скрипты управления..."

cat > start_bot.sh << EOF
#!/bin/bash
cd ~/domain/bot.kotovod.ru
if [ -d "venv" ]; then
    source venv/bin/activate
fi
nohup $PYTHON_CMD lamoda_monitor_bot.py > bot_output.log 2>&1 &
echo \$! > bot.pid
echo "✅ Бот запущен! PID: \$(cat bot.pid)"
EOF

cat > stop_bot.sh << 'EOF'
#!/bin/bash
cd ~/domain/bot.kotovod.ru
if [ -f bot.pid ]; then
    PID=$(cat bot.pid)
    kill $PID 2>/dev/null && echo "✅ Бот остановлен" || echo "⚠️  Процесс уже завершен"
    rm bot.pid
else
    pkill -f lamoda_monitor_bot.py && echo "✅ Процесс остановлен" || echo "⚠️  Процесс не найден"
fi
EOF

cat > restart_bot.sh << 'EOF'
#!/bin/bash
cd ~/domain/bot.kotovod.ru
./stop_bot.sh
sleep 2
./start_bot.sh
EOF

cat > status_bot.sh << 'EOF'
#!/bin/bash
cd ~/domain/bot.kotovod.ru
if [ -f bot.pid ]; then
    PID=$(cat bot.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ Бот работает (PID: $PID)"
        echo ""
        echo "📊 Последние 10 строк лога:"
        tail -n 10 lamoda_monitor.log
    else
        echo "❌ Бот не работает (PID файл есть, но процесс завершен)"
    fi
else
    echo "⚠️  PID файл не найден"
    if pgrep -f lamoda_monitor_bot.py > /dev/null; then
        echo "⚠️  Но процесс запущен: PID $(pgrep -f lamoda_monitor_bot.py)"
    else
        echo "❌ Бот не запущен"
    fi
fi
EOF

chmod +x start_bot.sh stop_bot.sh restart_bot.sh status_bot.sh

echo "✅ Скрипты созданы"

# Останавливаем старые процессы
echo ""
echo "🛑 Останавливаем старые процессы..."
pkill -f lamoda_monitor_bot.py 2>/dev/null || echo "Старых процессов нет"
sleep 2

# Запускаем бота
echo ""
echo "🚀 Запускаем бота..."
./start_bot.sh

sleep 3

# Проверяем запуск
echo ""
echo "🔍 Проверяем запуск..."
./status_bot.sh

echo ""
echo "================================"
echo "📁 ФАЙЛЫ В: ~/domain/bot.kotovod.ru/"
echo "================================"
echo ""
echo "📊 Команды управления:"
echo "  cd ~/domain/bot.kotovod.ru"
echo "  ./start_bot.sh      # Запуск"
echo "  ./stop_bot.sh       # Остановка"
echo "  ./restart_bot.sh    # Перезапуск"
echo "  ./status_bot.sh     # Статус"
echo "  tail -f lamoda_monitor.log  # Логи"
echo ""

# Показываем первые строки лога
if [ -f bot_output.log ]; then
    echo "📝 Первые строки лога:"
    head -n 30 bot_output.log
fi

ENDSSH

echo ""
echo "🎉 ДЕПЛОЙ ЗАВЕРШЕН!"
echo ""
echo "📁 Все файлы в: domain/bot.kotovod.ru/"
echo "📱 Проверьте Telegram!"
echo ""

