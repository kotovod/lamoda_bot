#!/usr/bin/env python3
"""
Примеры использования Lamoda Parser
"""

from lamoda_final_parser import parse_lamoda_products
import json


def example_1_basic():
    """Пример 1: Базовое использование"""
    print("="*80)
    print("ПРИМЕР 1: Базовое получение товаров")
    print("="*80 + "\n")
    
    url = "https://www.lamoda.ru/b/1163/brand-adidasoriginals/?sort=new"
    products = parse_lamoda_products(url)
    
    print(f"Получено товаров: {len(products)}\n")
    
    # Показываем первые 5
    for i, product in enumerate(products[:5], 1):
        print(f"{i}. {product.get('name', 'N/A')}")
        print(f"   Артикул: {product.get('sku', 'N/A')}")
        print()


def example_2_filter_by_category():
    """Пример 2: Фильтрация по категории"""
    print("="*80)
    print("ПРИМЕР 2: Фильтрация товаров по названию")
    print("="*80 + "\n")
    
    url = "https://www.lamoda.ru/b/1163/brand-adidasoriginals/?sort=new"
    products = parse_lamoda_products(url)
    
    # Ищем только кроссовки
    sneakers = [p for p in products if 'кроссов' in p.get('name', '').lower() or 'кед' in p.get('name', '').lower()]
    
    print(f"Найдено кроссовок и кед: {len(sneakers)}\n")
    
    for i, product in enumerate(sneakers[:5], 1):
        print(f"{i}. {product.get('name', 'N/A')}")
        print(f"   Артикул: {product.get('sku', 'N/A')}")
        print()


def example_3_save_custom():
    """Пример 3: Сохранение в кастомный формат"""
    print("="*80)
    print("ПРИМЕР 3: Сохранение в упрощенном формате")
    print("="*80 + "\n")
    
    url = "https://www.lamoda.ru/b/1163/brand-adidasoriginals/?sort=new"
    products = parse_lamoda_products(url)
    
    # Создаем упрощенный формат
    simplified = []
    for product in products:
        if product.get('name') and product.get('sku'):
            simplified.append({
                'название': product.get('name'),
                'артикул': product.get('sku'),
                'бренд': product.get('brand', {}).get('name') if isinstance(product.get('brand'), dict) else product.get('brand'),
            })
    
    # Сохраняем
    with open('товары_упрощенный.json', 'w', encoding='utf-8') as f:
        json.dump(simplified, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Сохранено {len(simplified)} товаров в 'товары_упрощенный.json'")
    print("\nПервые 3 товара:")
    for i, item in enumerate(simplified[:3], 1):
        print(f"{i}. {item['название']} ({item['артикул']})")


def example_4_statistics():
    """Пример 4: Статистика по товарам"""
    print("="*80)
    print("ПРИМЕР 4: Статистика по товарам")
    print("="*80 + "\n")
    
    url = "https://www.lamoda.ru/b/1163/brand-adidasoriginals/?sort=new"
    products = parse_lamoda_products(url)
    
    # Считаем категории
    categories = {}
    for product in products:
        name = product.get('name', '')
        if name and name not in ['adidas Originals', 'price']:
            # Простое определение категории по ключевым словам
            if any(word in name.lower() for word in ['кроссов', 'кед', 'сланц', 'сабо']):
                category = 'Обувь'
            elif any(word in name.lower() for word in ['футбол', 'худи', 'свитшот', 'олимпийк', 'куртк', 'ветровк']):
                category = 'Одежда'
            elif any(word in name.lower() for word in ['носки', 'шапка']):
                category = 'Аксессуары'
            else:
                category = 'Другое'
            
            categories[category] = categories.get(category, 0) + 1
    
    print("Распределение по категориям:\n")
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: {count} товаров")


def main():
    """Запуск всех примеров"""
    try:
        example_1_basic()
        print("\n")
        
        example_2_filter_by_category()
        print("\n")
        
        example_3_save_custom()
        print("\n")
        
        example_4_statistics()
        print("\n")
        
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()

