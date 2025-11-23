#!/usr/bin/env python3
"""
Простой и рабочий парсер для Lamoda
Выводит информацию о товарах, которую удалось извлечь
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from typing import List, Dict


def fetch_lamoda_page(url: str) -> str:
    """Загружает страницу Lamoda"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9',
        'Connection': 'keep-alive',
    }
    
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return response.text


def extract_json_ld(html: str) -> List[Dict]:
    """Извлекает структурированные данные JSON-LD со страницы"""
    soup = BeautifulSoup(html, 'html.parser')
    products = []
    
    # Ищем все JSON-LD скрипты
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string)
            
            # ItemList - список товаров
            if isinstance(data, dict) and data.get('@type') == 'ItemList':
                for item in data.get('itemListElement', []):
                    product_data = item.get('item', {})
                    if product_data:
                        offers = product_data.get('offers', {})
                        brand = product_data.get('brand', {})
                        
                        product = {
                            'name': product_data.get('name'),
                            'brand': brand.get('name') if isinstance(brand, dict) else brand,
                            'sku': product_data.get('sku'),
                            'price': offers.get('price'),
                            'currency': offers.get('priceCurrency', 'RUB'),
                            'url': product_data.get('url'),
                            'image': product_data.get('image'),
                        }
                        products.append(product)
                        
        except (json.JSONDecodeError, KeyError, AttributeError):
            continue
    
    return products


def extract_from_nextjs_data(html: str) -> List[Dict]:
    """Извлекает данные из Next.js __NEXT_DATA__"""
    products = []
    
    # Ищем __NEXT_DATA__
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', html, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(1))
            
            # Ищем товары в props.pageProps или других местах
            def find_products_recursive(obj, depth=0):
                if depth > 10:
                    return []
                
                found = []
                if isinstance(obj, dict):
                    # Проверяем, похоже ли на товар
                    if 'sku' in obj or ('name' in obj and 'price' in obj):
                        found.append(obj)
                    
                    # Рекурсивно ищем в значениях
                    for key, value in obj.items():
                        if key in ['products', 'items', 'catalog', 'data']:
                            if isinstance(value, list):
                                for item in value:
                                    found.extend(find_products_recursive(item, depth + 1))
                            else:
                                found.extend(find_products_recursive(value, depth + 1))
                        elif isinstance(value, (dict, list)):
                            found.extend(find_products_recursive(value, depth + 1))
                            
                elif isinstance(obj, list):
                    for item in obj:
                        found.extend(find_products_recursive(item, depth + 1))
                
                return found
            
            products = find_products_recursive(data)
            
        except json.JSONDecodeError:
            pass
    
    return products


def save_html_for_analysis(html: str, filename: str = 'lamoda_page.html'):
    """Сохраняет HTML для анализа"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✓ HTML сохранен в {filename} для анализа")


def main():
    url = "https://www.lamoda.ru/b/1163/brand-adidasoriginals/?sort=new"
    
    print("="*80)
    print("Lamoda Parser - Простая версия")
    print("="*80)
    print(f"\nURL: {url}\n")
    
    try:
        # Загружаем страницу
        print("⏳ Загрузка страницы...")
        html = fetch_lamoda_page(url)
        print(f"✓ Страница загружена ({len(html)} байт)\n")
        
        # Сохраняем для анализа
        save_html_for_analysis(html)
        
        # Пытаемся извлечь данные
        print("⏳ Извлечение данных из JSON-LD...")
        products = extract_json_ld(html)
        
        if not products:
            print("⚠ JSON-LD не содержит товаров, пробуем Next.js данные...")
            products = extract_from_nextjs_data(html)
        
        # Результаты
        print(f"\n{'='*80}")
        if products:
            print(f"✓ Найдено товаров: {len(products)}")
            print(f"{'='*80}\n")
            
            # Выводим первые 20 товаров
            for i, product in enumerate(products[:20], 1):
                print(f"{i}. {product.get('name', 'N/A')}")
                
                if product.get('brand'):
                    print(f"   Бренд: {product['brand']}")
                
                if product.get('sku'):
                    print(f"   Артикул: {product['sku']}")
                
                price = product.get('price', 'N/A')
                currency = product.get('currency', '')
                print(f"   Цена: {price} {currency}")
                
                if product.get('url'):
                    print(f"   URL: {product['url']}")
                
                print(f"{'-'*80}\n")
            
            if len(products) > 20:
                print(f"... и еще {len(products) - 20} товаров\n")
            
            # Сохраняем в JSON
            with open('lamoda_products_final.json', 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            print(f"✓ Все товары сохранены в lamoda_products_final.json\n")
            
        else:
            print("✗ Не удалось извлечь товары")
            print(f"{'='*80}\n")
            print("Возможные причины:")
            print("  • Сайт использует защиту от ботов (Cloudflare, reCAPTCHA)")
            print("  • Требуется JavaScript для загрузки контента")
            print("  • Изменилась структура сайта")
            print("\nРекомендации:")
            print("  • Проверьте файл lamoda_page.html")
            print("  • Используйте браузерное расширение или Selenium")
            print("  • Обратитесь к официальному API (если доступен)\n")
            
    except Exception as e:
        print(f"\n✗ Ошибка: {e}\n")


if __name__ == "__main__":
    main()

