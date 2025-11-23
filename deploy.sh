#!/bin/bash
# Скрипт автоматического деплоя бота на сервер

echo "============================================"
echo "🚀 ДЕПЛОЙ LAMODA MONITOR BOT НА СЕРВЕР"
echo "============================================"
echo ""

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Определяем имя пользователя
CURRENT_USER=$(whoami)
WORK_DIR="$HOME/Lamoda_bot"

echo "📍 Текущий пользователь: $CURRENT_USER"
echo "📁 Директория установки: $WORK_DIR"
echo ""

# 1. Создание директории
echo "1️⃣  Создание директории проекта..."
mkdir -p "$WORK_DIR"
cd "$WORK_DIR" || exit 1
echo -e "${GREEN}✅ Директория создана${NC}"
echo ""

# 2. Клонирование/копирование файлов
echo "2️⃣  Копирование файлов проекта..."
echo "   (Файлы должны быть загружены вручную или через git)"
echo ""

# 3. Установка Python и зависимостей
echo "3️⃣  Проверка Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ Python установлен: $PYTHON_VERSION${NC}"
else
    echo -e "${YELLOW}⚠️  Python не найден. Устанавливаем...${NC}"
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3 python3-pip
    fi
fi
echo ""

# 4. Создание виртуального окружения
echo "4️⃣  Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate
echo -e "${GREEN}✅ Виртуальное окружение создано${NC}"
echo ""

# 5. Установка зависимостей
echo "5️⃣  Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✅ Зависимости установлены${NC}"
echo ""

# 6. Настройка systemd service
echo "6️⃣  Настройка systemd service..."

# Создаем service файл с правильными путями
cat > lamoda-monitor.service << EOF
[Unit]
Description=Lamoda Monitor Bot - New Products Notifier
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$WORK_DIR
ExecStart=$WORK_DIR/venv/bin/python $WORK_DIR/lamoda_monitor_bot.py
Restart=always
RestartSec=10

# Логирование
StandardOutput=append:$WORK_DIR/bot_output.log
StandardError=append:$WORK_DIR/bot_error.log

[Install]
WantedBy=multi-user.target
EOF

echo "   Копируем service в systemd..."
sudo cp lamoda-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
echo -e "${GREEN}✅ Service настроен${NC}"
echo ""

# 7. Включение и запуск
echo "7️⃣  Запуск бота..."
sudo systemctl enable lamoda-monitor
sudo systemctl start lamoda-monitor
echo -e "${GREEN}✅ Бот запущен!${NC}"
echo ""

# 8. Проверка статуса
echo "8️⃣  Проверка статуса..."
sleep 2
sudo systemctl status lamoda-monitor --no-pager
echo ""

echo "============================================"
echo "🎉 ДЕПЛОЙ ЗАВЕРШЕН!"
echo "============================================"
echo ""
echo "📊 Полезные команды:"
echo "   Статус:      sudo systemctl status lamoda-monitor"
echo "   Логи:        tail -f $WORK_DIR/lamoda_monitor.log"
echo "   Остановить:  sudo systemctl stop lamoda-monitor"
echo "   Запустить:   sudo systemctl start lamoda-monitor"
echo "   Рестарт:     sudo systemctl restart lamoda-monitor"
echo ""
echo "📱 Проверьте Telegram - должно прийти сообщение о запуске!"
echo ""

