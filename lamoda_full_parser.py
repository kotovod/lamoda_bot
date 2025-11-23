#!/usr/bin/env python3
"""
Улучшенный парсер Lamoda - получает ВСЕ товары с пагинацией
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from typing import List, Dict
import time


def get_all_products_with_pagination(brand_id: str = "1163", max_pages: int = None) -> List[Dict]:
    """
    Получает все товары используя пагинацию
    
    Args:
        brand_id: ID бренда
        max_pages: Максимум страниц (None = все)
    """
    
    base_url = "https://www.lamoda.ru/b/{}/brand-adidasoriginals/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
    }
    
    all_products = []
    page = 1
    
    print(f"🔍 Начинаем сбор всех товаров...\n")
    
    while True:
        if max_pages and page > max_pages:
            break
            
        # URL с параметром страницы
        url = f"{base_url.format(brand_id)}?page={page}&sort=new"
        
        print(f"📄 Страница {page}... ", end='', flush=True)
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Извлекаем товары
            products = extract_products_from_html(response.text)
            
            if not products:
                print("❌ Товары не найдены, конец пагинации")
                break
            
            # Фильтруем валидные товары
            valid_products = [
                p for p in products 
                if p.get('name') and 
                p.get('name') not in ['adidas Originals', 'price'] and
                p.get('sku')
            ]
            
            if not valid_products:
                print("❌ Нет валидных товаров, конец пагинации")
                break
            
            all_products.extend(valid_products)
            print(f"✅ Получено: {len(valid_products)} товаров (всего: {len(all_products)})")
            
            # Проверяем, есть ли еще страницы
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем индикатор последней страницы или общее количество
            # Если товаров на странице меньше обычного - это последняя страница
            if len(valid_products) < 10:  # Обычно на странице больше товаров
                print("\n⚠️ Похоже, это последняя страница")
                break
            
            page += 1
            time.sleep(0.5)  # Небольшая задержка между запросами
            
        except requests.RequestException as e:
            print(f"❌ Ошибка: {e}")
            break
    
    return all_products


def extract_products_from_html(html: str) -> List[Dict]:
    """Извлекает товары из HTML"""
    soup = BeautifulSoup(html, 'html.parser')
    products = []
    
    # Метод 1: JSON в скриптах
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string and ('sku' in script.string or 'brand' in script.string):
            try:
                # Ищем JSON объекты
                matches = re.findall(r'\{[^{}]*"sku"[^{}]*\}', script.string)
                for match in matches:
                    try:
                        data = json.loads(match)
                        if data.get('sku'):
                            products.append(data)
                    except:
                        continue
            except:
                continue
    
    # Метод 2: JSON-LD
    for script_tag in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script_tag.string)
            if data.get('@type') == 'ItemList':
                for item in data.get('itemListElement', []):
                    product = item.get('item', {})
                    if product:
                        products.append(product)
        except:
            continue
    
    return products


def print_products_summary(products: List[Dict]):
    """Выводит краткую сводку"""
    print("\n" + "="*80)
    print(f"📦 ИТОГО ПОЛУЧЕНО ТОВАРОВ: {len(products)}")
    print("="*80 + "\n")
    
    # Статистика по категориям
    categories = {
        'Обувь': ['кед', 'кроссов', 'сланц', 'сабо', 'ботин'],
        'Одежда': ['футбол', 'худи', 'свитшот', 'олимпийк', 'куртк', 'брюки', 'шорт', 'ветровк'],
        'Аксессуары': ['носки', 'шапк', 'кепк', 'сумк', 'рюкзак']
    }
    
    stats = {}
    for product in products:
        name = product.get('name', '').lower()
        categorized = False
        
        for category, keywords in categories.items():
            if any(keyword in name for keyword in keywords):
                stats[category] = stats.get(category, 0) + 1
                categorized = True
                break
        
        if not categorized:
            stats['Другое'] = stats.get('Другое', 0) + 1
    
    print("📊 СТАТИСТИКА ПО КАТЕГОРИЯМ:\n")
    for category, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        bar = '█' * (count // 10 if count > 10 else count)
        print(f"  {category:15s}: {bar} {count}")
    
    print("\n" + "="*80)
    print("ПЕРВЫЕ 10 ТОВАРОВ:\n")
    
    for i, product in enumerate(products[:10], 1):
        brand_info = product.get('brand', {})
        if isinstance(brand_info, dict):
            brand = brand_info.get('name', 'N/A')
        else:
            brand = brand_info
        
        print(f"  {i:2d}. {product.get('name', 'N/A')}")
        if brand != 'N/A':
            print(f"      Бренд: {brand}")
        print(f"      Артикул: {product.get('sku', 'N/A')}")
        print()


def save_to_json(products: List[Dict], filename: str):
    """Сохраняет в JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Данные сохранены в {filename}")


def main():
    print("="*80)
    print("LAMODA PARSER - Полная версия (ВСЕ товары)")
    print("="*80)
    print("\n🎯 Цель: Получить ВСЕ товары с сайта")
    print("📍 Категория: Adidas Originals\n")
    
    # Получаем все товары
    # Для теста ограничим 30 страницами (обычно ~50-60 товаров на странице)
    products = get_all_products_with_pagination(brand_id="1163", max_pages=30)
    
    if products:
        print_products_summary(products)
        save_to_json(products, 'lamoda_all_products.json')
        
        print("\n" + "="*80)
        print(f"✅ УСПЕШНО! Получено {len(products)} товаров из ~1592")
        print("="*80 + "\n")
    else:
        print("\n❌ Не удалось получить товары")


if __name__ == "__main__":
    main()

