#!/usr/bin/env python3
"""
РАБОЧАЯ ВЕРСИЯ - Получение ВСЕХ товаров через пагинацию
Использует проверенный метод из lamoda_final_parser.py
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from typing import List, Dict
import time


def parse_page_products(page: int = 1) -> List[Dict]:
    """Парсит товары с одной страницы (используя проверенный метод)"""
    
    url = f"https://www.lamoda.ru/b/1163/brand-adidasoriginals/?page={page}&sort=new"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        html = response.text
        
        products = []
        
        # ===== МЕТОД 1: window.dataLayer (ПРОВЕРЕННЫЙ РАБОЧИЙ МЕТОД) =====
        dataLayer_match = re.search(r'window\.dataLayer\s*=\s*\[(.*?)\];', html, re.DOTALL)
        if dataLayer_match:
            try:
                dataLayer_str = '[' + dataLayer_match.group(1) + ']'
                dataLayer_str = re.sub(r"'([^']*)'", r'"\1"', dataLayer_str)
                dataLayer = json.loads(dataLayer_str)
                
                for entry in dataLayer:
                    if 'ecommerce' in entry:
                        ecom = entry['ecommerce']
                        if 'impressions' in ecom:
                            for item in ecom['impressions']:
                                products.append({
                                    'name': item.get('name'),
                                    'brand': item.get('brand'),
                                    'category': item.get('category'),
                                    'price': item.get('price'),
                                    'sku': item.get('id'),
                                    'id': item.get('id'),
                                    'url': f"https://www.lamoda.ru/p/{item.get('id')}/"
                                })
            except Exception as e:
                pass
        
        # ===== МЕТОД 2: JSON в скриптах =====
        json_pattern = r'<script[^>]*>(.*?)</script>'
        scripts = re.findall(json_pattern, html, re.DOTALL)
        
        for script in scripts:
            if 'products' in script or 'items' in script:
                try:
                    json_objects = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', script)
                    for json_str in json_objects:
                        if 'sku' in json_str or 'name' in json_str:
                            try:
                                data = json.loads(json_str)
                                if isinstance(data, dict) and 'name' in data:
                                    products.append(data)
                            except:
                                continue
                except:
                    continue
        
        # ===== МЕТОД 3: JSON-LD =====
        for script_tag in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script_tag.string)
                if data.get('@type') == 'ItemList':
                    for item in data.get('itemListElement', []):
                        product = item.get('item', {})
                        if product:
                            offers = product.get('offers', {})
                            products.append({
                                'name': product.get('name'),
                                'brand': product.get('brand', {}).get('name') if isinstance(product.get('brand'), dict) else product.get('brand'),
                                'sku': product.get('sku'),
                                'price': offers.get('price'),
                                'currency': offers.get('priceCurrency', 'RUB'),
                                'url': product.get('url'),
                                'image': product.get('image')
                            })
            except:
                continue
        
        return products
        
    except Exception as e:
        return []


def get_all_products_paginated(max_pages: int = 30) -> List[Dict]:
    """Собирает товары со всех страниц"""
    
    all_products = []
    seen_skus = set()
    empty_pages = 0
    
    print("="*80)
    print("🚀 СБОР ВСЕХ ТОВАРОВ LAMODA (ПАГИНАЦИЯ)")
    print("="*80)
    print(f"\n📍 Бренд: Adidas Originals")
    print(f"🎯 Ожидается: ~1591 товар")
    print(f"📄 Максимум страниц: {max_pages}\n")
    print("="*80 + "\n")
    
    for page in range(1, max_pages + 1):
        print(f"📄 Страница {page:2d}... ", end='', flush=True)
        
        products = parse_page_products(page)
        
        if not products:
            empty_pages += 1
            print(f"⚠️  Нет товаров (пустых страниц подряд: {empty_pages})")
            if empty_pages >= 2:  # Если 2 страницы подряд пустые - конец
                print("\n⛔ Две пустые страницы подряд - завершаем сбор")
                break
            continue
        
        # Сбрасываем счетчик пустых страниц
        empty_pages = 0
        
        # Фильтруем уникальные валидные товары
        new_products = 0
        for product in products:
            sku = product.get('sku') or product.get('id')
            name = product.get('name', '')
            
            # Пропускаем мусор
            if name in ['adidas Originals', 'price', ''] or not sku:
                continue
            
            # Проверяем уникальность
            if sku not in seen_skus:
                seen_skus.add(sku)
                all_products.append(product)
                new_products += 1
        
        print(f"✅ +{new_products:3d} новых | Всего: {len(all_products):4d}")
        
        # Задержка между запросами
        time.sleep(0.3)
    
    return all_products


def print_summary(products: List[Dict]):
    """Выводит итоговую статистику"""
    print("\n" + "="*80)
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("="*80)
    print(f"\n✅ Всего уникальных товаров: {len(products)}")
    
    # Подсчет категорий
    categories = {'Обувь': 0, 'Одежда': 0, 'Аксессуары': 0, 'Другое': 0}
    
    keywords_map = {
        'Обувь': ['кед', 'кроссов', 'сланц', 'сабо', 'ботин', 'туфл'],
        'Одежда': ['футбол', 'худи', 'свитшот', 'олимпийк', 'куртк', 'брюки', 'шорт', 'ветровк', 'жилет'],
        'Аксессуары': ['носки', 'шапк', 'кепк', 'сумк', 'рюкзак', 'ремень']
    }
    
    for product in products:
        name = product.get('name', '').lower()
        categorized = False
        
        for category, keywords in keywords_map.items():
            if any(kw in name for kw in keywords):
                categories[category] += 1
                categorized = True
                break
        
        if not categorized:
            categories['Другое'] += 1
    
    print(f"\n📈 Распределение по категориям:\n")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            bar = '█' * (count // 30 if count > 30 else count // 3)
            print(f"   {cat:15s}: {bar:30s} {count:4d} ({count*100//len(products):2d}%)")
    
    # Примеры товаров
    print(f"\n📦 Примеры товаров (первые 20):\n")
    for i, product in enumerate(products[:20], 1):
        brand = product.get('brand', 'N/A')
        print(f"   {i:2d}. {product.get('name', 'N/A')}")
        if brand != 'N/A':
            print(f"       Бренд: {brand}")
        print(f"       SKU: {product.get('sku') or product.get('id', 'N/A')}")
        if product.get('price'):
            print(f"       Цена: {product.get('price')} ₽")
        print()
    
    if len(products) > 20:
        print(f"   ... и еще {len(products) - 20} товаров\n")


def save_to_json(products: List[Dict], filename: str):
    """Сохраняет результаты в JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"💾 Данные сохранены в: {filename}")


def main():
    # Собираем товары со всех страниц
    products = get_all_products_paginated(max_pages=30)
    
    if products:
        print_summary(products)
        save_to_json(products, 'lamoda_all_products_complete.json')
        
        print("\n" + "="*80)
        expected = 1591
        percentage = (len(products) * 100) // expected
        print(f"🎉 УСПЕШНО! Получено {len(products)} из ~{expected} товаров ({percentage}%)")
        print("="*80 + "\n")
    else:
        print("\n❌ Не удалось получить товары")


if __name__ == "__main__":
    main()

