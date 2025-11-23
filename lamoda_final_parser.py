#!/usr/bin/env python3
"""
Финальная рабочая версия парсера Lamoda
Использует встроенные данные страницы
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from typing import List, Dict


def parse_lamoda_products(url: str) -> List[Dict]:
    """Парсит товары с Lamoda"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    html = response.text
    
    products = []
    
    # Метод 1: Поиск в window.dataLayer (Google Tag Manager)
    dataLayer_match = re.search(r'window\.dataLayer\s*=\s*\[(.*?)\];', html, re.DOTALL)
    if dataLayer_match:
        try:
            # Пробуем распарсить dataLayer
            dataLayer_str = '[' + dataLayer_match.group(1) + ']'
            # Заменяем одинарные кавычки на двойные для JSON
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
                                'id': item.get('id'),
                                'url': f"https://www.lamoda.ru/p/{item.get('id')}/"
                            })
        except:
            pass
    
    # Метод 2: Поиск JSON встроенных данных
    json_pattern = r'<script[^>]*>(.*?)</script>'
    scripts = re.findall(json_pattern, html, re.DOTALL)
    
    for script in scripts:
        # Ищем паттерны с товарами
        if 'products' in script or 'items' in script:
            try:
                # Пытаемся найти JSON объекты
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
    
    # Метод 3: HTML meta tags и структурированные данные
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


def print_products(products: List[Dict]):
    """Выводит список товаров"""
    print("\n" + "="*80)
    print(f"НАЙДЕНО ТОВАРОВ: {len(products)}")
    print("="*80 + "\n")
    
    for i, product in enumerate(products[:30], 1):  # Показываем первые 30
        print(f"{i}. {product.get('name', 'N/A')}")
        
        # Обработка бренда (может быть строкой или словарем)
        if product.get('brand'):
            brand = product['brand']
            if isinstance(brand, dict):
                brand_name = brand.get('name', 'N/A')
            else:
                brand_name = brand
            print(f"   Бренд: {brand_name}")
        
        # Артикул
        if product.get('sku') or product.get('id'):
            sku = product.get('sku') or product.get('id')
            if sku not in ['1163', 'price']:  # Фильтруем некорректные данные
                print(f"   Артикул: {sku}")
        
        # Цена
        if product.get('price'):
            currency = product.get('currency', 'RUB')
            print(f"   Цена: {product['price']} {currency}")
        
        # Категория
        if product.get('category'):
            print(f"   Категория: {product['category']}")
        
        # URL
        if product.get('url') and not product['url'].startswith('/brand/'):
            url = product['url']
            if not url.startswith('http'):
                url = f"https://www.lamoda.ru{url}"
            print(f"   URL: {url}")
        
        print("-" * 80)
    
    if len(products) > 30:
        print(f"\n... и ещё {len(products) - 30} товаров\n")


def save_to_json(products: List[Dict], filename: str):
    """Сохраняет товары в JSON файл"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Данные сохранены в {filename}\n")


def main():
    url = "https://www.lamoda.ru/b/1163/brand-adidasoriginals/?sort=new"
    
    print("="*80)
    print("LAMODA PARSER - Финальная версия")
    print("="*80)
    print(f"\nURL: {url}")
    print("Загрузка данных...\n")
    
    products = parse_lamoda_products(url)
    
    if products:
        print_products(products)
        save_to_json(products, 'lamoda_products_working.json')
        print(f"{'='*80}")
        print(f"✓ УСПЕШНО! Получено {len(products)} товаров")
        print(f"{'='*80}\n")
    else:
        print("\n" + "="*80)
        print("⚠ НЕ УДАЛОСЬ ИЗВЛЕЧЬ ТОВАРЫ")
        print("="*80)
        print("\nСайт Lamoda использует сложную защиту от парсинга.")
        print("Для получения данных рекомендуется:")
        print("  1. Использовать официальный API (если доступен)")
        print("  2. Использовать Selenium с реальным браузером")
        print("  3. Использовать специализированные сервисы парсинга\n")


if __name__ == "__main__":
    main()

