#!/usr/bin/env python3
"""
ФИНАЛЬНАЯ ВЕРСИЯ - Получение ВСЕХ товаров через пагинацию
Парсит страницы 1, 2, 3... пока есть товары
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from typing import List, Dict
import time


def parse_lamoda_page(page: int = 1) -> List[Dict]:
    """Парсит одну страницу и возвращает товары"""
    
    url = f"https://www.lamoda.ru/b/1163/brand-adidasoriginals/?page={page}&sort=new"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'ru-RU,ru;q=0.9',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        html = response.text
        
        # Извлекаем товары
        products = []
        
        # Метод: поиск JSON объектов с товарами в скриптах
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
        
        for script in scripts:
            if 'sku' in script and 'brand' in script:
                # Ищем JSON объекты с товарами
                # Пробуем найти массивы товаров
                array_matches = re.findall(r'\[(\{[^\[\]]*"sku"[^\[\]]*\}(?:,\s*\{[^\[\]]*"sku"[^\[\]]*\})*)\]', script)
                
                for match in array_matches:
                    # Пробуем распарсить массив
                    try:
                        items_json = '[' + match + ']'
                        items = json.loads(items_json)
                        for item in items:
                            if isinstance(item, dict) and item.get('sku'):
                                products.append(item)
                    except:
                        continue
                
                # Также ищем отдельные объекты
                obj_matches = re.findall(r'\{[^{}]*"sku"\s*:\s*"([^"]+)"[^{}]*\}', script)
                for match in obj_matches:
                    # Пробуем найти полный объект
                    try:
                        full_match = re.search(r'\{[^{}]*"sku"\s*:\s*"' + re.escape(match) + r'"[^{}]*\}', script)
                        if full_match:
                            obj = json.loads(full_match.group(0))
                            if obj.get('sku'):
                                products.append(obj)
                    except:
                        continue
        
        return products
        
    except Exception as e:
        print(f"      ❌ Ошибка: {e}")
        return []


def get_all_products(max_pages: int = 50) -> List[Dict]:
    """Получает товары со всех страниц"""
    
    all_products = []
    seen_skus = set()
    
    print("="*80)
    print("🚀 ПОЛНЫЙ СБОР ТОВАРОВ С LAMODA")
    print("="*80)
    print(f"\n📍 Категория: Adidas Originals")
    print(f"🎯 Цель: Получить максимум товаров\n")
    print("="*80 + "\n")
    
    for page in range(1, max_pages + 1):
        print(f"📄 Страница {page:2d}... ", end='', flush=True)
        
        products = parse_lamoda_page(page)
        
        if not products:
            print("❌ Товары не найдены - конец")
            break
        
        # Фильтруем уникальные товары
        new_products = []
        for product in products:
            sku = product.get('sku')
            name = product.get('name', '')
            
            # Пропускаем мусорные данные
            if name in ['adidas Originals', 'price', ''] or not sku:
                continue
            
            # Проверяем уникальность
            if sku and sku not in seen_skus:
                seen_skus.add(sku)
                new_products.append(product)
        
        if new_products:
            all_products.extend(new_products)
            print(f"✅ Получено: {len(new_products):3d} новых товаров (всего: {len(all_products):4d})")
        else:
            print(f"⚠️  Нет новых товаров (возможно, конец)")
            # Пробуем еще 2 страницы для уверенности
            if page > 3:
                break
        
        # Задержка между запросами
        time.sleep(0.5)
    
    return all_products


def print_summary(products: List[Dict]):
    """Выводит статистику"""
    print("\n" + "="*80)
    print(f"📦 ИТОГОВАЯ СТАТИСТИКА")
    print("="*80)
    print(f"\n✅ Всего получено уникальных товаров: {len(products)}")
    
    # Категории
    categories = {
        'Обувь': 0,
        'Одежда': 0,
        'Аксессуары': 0,
        'Другое': 0
    }
    
    obuvь_keywords = ['кед', 'кроссов', 'сланц', 'сабо', 'ботин', 'туфл']
    odezhda_keywords = ['футбол', 'худи', 'свитшот', 'олимпийк', 'куртк', 'брюки', 'шорт', 'ветровк', 'жилет', 'платье', 'юбк']
    aksessuary_keywords = ['носки', 'шапк', 'кепк', 'сумк', 'рюкзак', 'ремень', 'часы', 'очки']
    
    for product in products:
        name = product.get('name', '').lower()
        if any(kw in name for kw in obuvь_keywords):
            categories['Обувь'] += 1
        elif any(kw in name for kw in odezhda_keywords):
            categories['Одежда'] += 1
        elif any(kw in name for kw in aksessuary_keywords):
            categories['Аксессуары'] += 1
        else:
            categories['Другое'] += 1
    
    print(f"\n📊 По категориям:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            bar = '█' * (count // 20 if count > 20 else count)
            print(f"   {cat:15s}: {bar} {count}")
    
    # Примеры товаров
    print(f"\n📦 Примеры товаров (первые 15):\n")
    for i, product in enumerate(products[:15], 1):
        brand = product.get('brand', {})
        brand_name = brand.get('name') if isinstance(brand, dict) else brand
        
        print(f"   {i:2d}. {product.get('name', 'N/A')}")
        if brand_name:
            print(f"       Бренд: {brand_name}")
        print(f"       SKU: {product.get('sku', 'N/A')}")
        print()
    
    if len(products) > 15:
        print(f"   ... и еще {len(products) - 15} товаров")


def save_to_json(products: List[Dict], filename: str):
    """Сохраняет в JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Данные сохранены в: {filename}")


def main():
    # Собираем все товары
    products = get_all_products(max_pages=50)
    
    if products:
        # Выводим статистику
        print_summary(products)
        
        # Сохраняем
        save_to_json(products, 'lamoda_all_products_final.json')
        
        print("\n" + "="*80)
        print(f"🎉 ГОТОВО! Получено {len(products)} товаров")
        print("="*80 + "\n")
    else:
        print("\n❌ Не удалось получить товары")


if __name__ == "__main__":
    main()

