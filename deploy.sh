#!/bin/bash

# ========================================
# Скрипт для переноса Lamoda Bot на сервер
# ========================================

echo "🚀 ПЕРЕНОС LAMODA BOT НА СЕРВЕР"
echo "================================"
echo ""

# Запрашиваем данные сервера
read -p "📍 Введите IP адрес сервера: " SERVER_IP
read -p "👤 Введите username (обычно root/ubuntu): " SERVER_USER
read -p "🔌 Введите SSH порт (обычно 22): " SERVER_PORT

# Проверка подключения
echo ""
echo "🔍 Проверяем подключение к серверу..."
ssh -p $SERVER_PORT $SERVER_USER@$SERVER_IP "echo '✅ Подключение успешно!'" || {
    echo "❌ Не удалось подключиться к серверу"
    echo "Проверьте IP, username и порт"
    exit 1
}

echo ""
echo "📦 Архивируем проект..."
cd /Users/kotovod/Desktop
tar --exclude='venv' --exclude='*.pyc' --exclude='__pycache__' --exclude='.git' \
    -czf Lamoda_bot_deploy.tar.gz Lamoda_bot/

echo "✅ Архив создан: Lamoda_bot_deploy.tar.gz"

echo ""
echo "⬆️  Загружаем на сервер..."
scp -P $SERVER_PORT Lamoda_bot_deploy.tar.gz $SERVER_USER@$SERVER_IP:~

echo "✅ Файлы загружены!"

echo ""
echo "🔧 Настраиваем на сервере..."

# Выполняем команды на сервере
ssh -p $SERVER_PORT $SERVER_USER@$SERVER_IP << 'ENDSSH'

echo "📂 Распаковываем архив..."
cd ~
tar -xzf Lamoda_bot_deploy.tar.gz
cd Lamoda_bot

echo "🐍 Устанавливаем Python зависимости..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

echo "📦 Создаем виртуальное окружение..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo ""
echo "👤 Определяем текущего пользователя..."
CURRENT_USER=$(whoami)
HOME_DIR=$(eval echo ~$CURRENT_USER)

echo "   Username: $CURRENT_USER"
echo "   Home dir: $HOME_DIR"

# Обновляем service файл с правильными путями
echo "⚙️  Настраиваем systemd service..."
sed -i "s|YOUR_USERNAME|$CURRENT_USER|g" lamoda-monitor.service
sed -i "s|/home/YOUR_USERNAME|$HOME_DIR|g" lamoda-monitor.service

echo "📋 Устанавливаем service..."
sudo cp lamoda-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable lamoda-monitor

echo ""
echo "🧪 Тестируем бота..."
python test_bot.py

echo ""
echo "🚀 Запускаем бота как сервис..."
sudo systemctl start lamoda-monitor

echo ""
echo "✅ Проверяем статус..."
sudo systemctl status lamoda-monitor --no-pager -l

echo ""
echo "================================"
echo "✅ УСТАНОВКА ЗАВЕРШЕНА!"
echo "================================"
echo ""
echo "📊 Полезные команды:"
echo "  sudo systemctl status lamoda-monitor  # Статус"
echo "  tail -f ~/Lamoda_bot/lamoda_monitor.log  # Логи"
echo "  sudo systemctl restart lamoda-monitor  # Перезапуск"
echo ""

ENDSSH

echo ""
echo "🎉 ВСЁ ГОТОВО!"
echo ""
echo "Бот работает на сервере 24/7"
echo "Проверьте Telegram - должно прийти сообщение о запуске"
echo ""

# Удаляем временный архив
rm /Users/kotovod/Desktop/Lamoda_bot_deploy.tar.gz

echo "💡 Для просмотра логов подключитесь к серверу:"
echo "   ssh -p $SERVER_PORT $SERVER_USER@$SERVER_IP"
echo "   tail -f ~/Lamoda_bot/lamoda_monitor.log"
