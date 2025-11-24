#!/bin/bash

# Подключаемся и проверяем что случилось
ssh roller25@roller25.myjino.ru << 'ENDSSH'

echo "🔍 ДИАГНОСТИКА ПРОБЛЕМЫ"
echo "======================="
echo ""

echo "1️⃣ Проверяем домашнюю директорию:"
ls -la ~ | head -20

echo ""
echo "2️⃣ Проверяем domain/bot.kotovod.ru/:"
ls -la ~/domain/bot.kotovod.ru/ 2>/dev/null || echo "❌ Директория не найдена"

echo ""
echo "3️⃣ Проверяем наличие temp_lamoda:"
ls -la ~/temp_lamoda/ 2>/dev/null || echo "temp_lamoda отсутствует"

echo ""
echo "4️⃣ Ищем файлы бота:"
find ~ -name "lamoda_monitor_bot.py" 2>/dev/null

echo ""
echo "======================="
echo "📊 ПЛАН ДЕЙСТВИЙ:"
echo "======================="

ENDSSH

