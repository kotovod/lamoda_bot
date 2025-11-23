#!/usr/bin/env python3
"""
Тестовый скрипт для проверки бота
Делает одну проверку и выходит
"""

import sys
sys.path.insert(0, '/Users/kotovod/Desktop/Lamoda_bot')

from lamoda_monitor_bot import (
    parse_lamoda_products,
    get_chat_id,
    notify_new_product,
    LAMODA_URL,
    logger
)

def test_bot():
    """Тестирует работу бота"""
    
    print("="*60)
    print("🧪 ТЕСТ LAMODA MONITOR BOT")
    print("="*60 + "\n")
    
    # 1. Тест парсинга
    print("1️⃣ Тестируем парсинг Lamoda...")
    products = parse_lamoda_products(LAMODA_URL)
    
    if products:
        print(f"   ✅ Получено товаров: {len(products)}")
        print(f"   📦 Первый товар: {products[0].get('name')}")
    else:
        print("   ❌ Не удалось получить товары")
        return
    
    print()
    
    # 2. Тест получения Chat ID
    print("2️⃣ Получаем Chat ID...")
    chat_id = get_chat_id()
    
    if chat_id:
        print(f"   ✅ Chat ID: {chat_id}")
    else:
        print("   ⚠️  Chat ID не найден")
        print("   💡 Отправьте любое сообщение боту:")
        print("      https://t.me/YOUR_BOT_NAME")
        return
    
    print()
    
    # 3. Тест отправки уведомления
    print("3️⃣ Тестируем отправку уведомления...")
    print(f"   Отправляем тестовое уведомление о товаре: {products[0].get('name')}")
    
    # Берем первый товар для теста
    test_product = products[0]
    
    notify_new_product(chat_id, test_product)
    
    print()
    print("="*60)
    print("✅ ТЕСТ ЗАВЕРШЕН!")
    print("="*60)
    print("\n💡 Проверьте Telegram - должно прийти тестовое уведомление\n")


if __name__ == "__main__":
    test_bot()

