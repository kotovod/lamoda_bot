#!/usr/bin/env python3
"""
ДЕМОНСТРАЦИЯ: Быстрый старт с Lamoda Parser
"""

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         LAMODA PARSER - QUICK START                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

Этот скрипт демонстрирует базовое использование парсера Lamoda.

""")

from lamoda_final_parser import parse_lamoda_products

# URL страницы с товарами
url = "https://www.lamoda.ru/b/1163/brand-adidasoriginals/?sort=new"

print(f"📡 Загрузка данных с: {url}\n")
print("⏳ Пожалуйста, подождите...\n")

# Получаем товары
products = parse_lamoda_products(url)

# Фильтруем валидные товары (убираем метаданные)
valid_products = [
    p for p in products 
    if p.get('name') and 
    p.get('name') not in ['adidas Originals', 'price'] and
    p.get('sku')
]

print("╔══════════════════════════════════════════════════════════════════════════════╗")
print(f"║ ✅ УСПЕШНО ПОЛУЧЕНО ТОВАРОВ: {len(valid_products):^47} ║")
print("╚══════════════════════════════════════════════════════════════════════════════╝\n")

# Показываем первые 10 товаров
print("📦 ПЕРВЫЕ 10 ТОВАРОВ:\n")
for i, product in enumerate(valid_products[:10], 1):
    brand_info = product.get('brand', {})
    if isinstance(brand_info, dict):
        brand = brand_info.get('name', 'N/A')
    else:
        brand = brand_info
    
    print(f"  {i:2d}. {product.get('name', 'N/A')}")
    print(f"      Бренд: {brand}")
    print(f"      Артикул: {product.get('sku', 'N/A')}")
    print()

if len(valid_products) > 10:
    print(f"  ... и ещё {len(valid_products) - 10} товаров\n")

# Статистика
print("═" * 80)
print("📊 БЫСТРАЯ СТАТИСТИКА:")
print("═" * 80)

categories = {
    'Обувь': ['кед', 'кроссов', 'сланц', 'сабо', 'ботин'],
    'Одежда': ['футбол', 'худи', 'свитшот', 'олимпийк', 'куртк', 'брюки', 'шорт', 'ветровк'],
    'Аксессуары': ['носки', 'шапк', 'кепк', 'сумк', 'рюкзак']
}

stats = {}
for product in valid_products:
    name = product.get('name', '').lower()
    categorized = False
    
    for category, keywords in categories.items():
        if any(keyword in name for keyword in keywords):
            stats[category] = stats.get(category, 0) + 1
            categorized = True
            break
    
    if not categorized:
        stats['Другое'] = stats.get('Другое', 0) + 1

for category, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
    bar = '█' * (count // 2)
    print(f"  {category:15s}: {bar} {count}")

print("\n" + "═" * 80)
print("\n✨ Данные сохранены в: lamoda_products_working.json")
print("\n💡 Для большего количества примеров запустите: python examples.py")
print("📖 Читайте README.md для подробной документации\n")

