#!/usr/bin/env python3
"""
Поиск настоящего API Lamoda через анализ сетевых запросов
"""

import requests
import json
from typing import List, Dict
import time


def try_catalog_api(page: int = 1) -> List[Dict]:
    """Пробуем разные варианты API каталога"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'ru-RU,ru;q=0.9',
        'x-requested-with': 'XMLHttpRequest',
        'Referer': 'https://www.lamoda.ru/'
    }
    
    # Вариант 1: Пагинация через параметр page
    urls_to_try = [
        f"https://www.lamoda.ru/b/1163/brand-adidasoriginals/?page={page}&sort=new",
        f"https://www.lamoda.ru/api/catalog/brand-adidasoriginals/?page={page}",
        f"https://www.lamoda.ru/api/v1/catalog?brand=1163&page={page}",
        f"https://www.lamoda.ru/catalogsearch/result/?brand=1163&p={page}",
    ]
    
    for url in urls_to_try:
        try:
            print(f"   Пробуем: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Пробуем распарсить как JSON
                try:
                    data = response.json()
                    print(f"   ✅ JSON ответ получен!")
                    return data
                except:
                    # Это HTML
                    if len(response.text) > 10000:
                        print(f"   ⚠️  HTML страница ({len(response.text)} байт)")
                    continue
            else:
                print(f"   ❌ Статус: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            continue
    
    return []


def analyze_page_structure():
    """Анализируем структуру страницы для поиска API endpoints"""
    
    print("="*80)
    print("АНАЛИЗ СТРУКТУРЫ СТРАНИЦЫ LAMODA")
    print("="*80 + "\n")
    
    url = "https://www.lamoda.ru/b/1163/brand-adidasoriginals/?sort=new"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    }
    
    print(f"📡 Загружаем: {url}\n")
    
    response = requests.get(url, headers=headers)
    html = response.text
    
    print(f"✅ Страница загружена ({len(html)} байт)\n")
    
    # Ищем упоминания API endpoints
    print("🔍 Поиск API endpoints в коде страницы:\n")
    
    api_patterns = [
        'api/',
        '/catalog',
        '/products',
        'endpoint',
        'ajax',
        '_next/data',
    ]
    
    found_apis = set()
    for pattern in api_patterns:
        import re
        matches = re.findall(f'["\']([^"\']*{pattern}[^"\']*)["\']', html)
        for match in matches[:5]:  # Первые 5 для каждого паттерна
            if len(match) > 10 and 'http' not in match:
                found_apis.add(match)
    
    if found_apis:
        print("Найденные потенциальные API paths:")
        for api in sorted(found_apis)[:20]:
            print(f"   • {api}")
    else:
        print("   ❌ API endpoints не найдены в HTML")
    
    # Ищем данные о пагинации
    print("\n🔍 Поиск информации о пагинации:\n")
    
    pagination_keywords = ['totalPages', 'totalItems', 'pageCount', 'total_pages', 'total', 'count']
    for keyword in pagination_keywords:
        if keyword in html:
            print(f"   ✅ Найдено: '{keyword}'")
            # Пробуем извлечь значение
            import re
            match = re.search(f'"{keyword}"\\s*:\\s*(\\d+)', html)
            if match:
                print(f"      Значение: {match.group(1)}")
    
    print("\n" + "="*80)
    print("ВЫВОД:")
    print("="*80)
    print("""
Lamoda использует современную архитектуру с серверным рендерингом (SSR).
Товары встроены в HTML при первой загрузке, а дополнительные подгружаются
через внутренние API при прокрутке.

Для получения ВСЕХ товаров нужно:
1. Использовать браузер (Selenium/Playwright) с прокруткой
2. Перехватывать XHR запросы в DevTools и эмулировать их
3. Использовать специализированные сервисы (ScrapingBee, Apify)

Текущий базовый парсер получает максимум данных из HTML (~60 товаров).
""")


def main():
    print("="*80)
    print("ПОИСК API LAMODA")
    print("="*80 + "\n")
    
    # Анализируем структуру
    analyze_page_structure()
    
    print("\n" + "="*80)
    print("ПРОБУЕМ РАЗЛИЧНЫЕ API ENDPOINTS")
    print("="*80 + "\n")
    
    # Пробуем разные варианты API
    for page in [1, 2]:
        print(f"\n📄 Страница {page}:")
        result = try_catalog_api(page)
        if result:
            print(f"   🎉 Получены данные!")
            break
        time.sleep(1)


if __name__ == "__main__":
    main()

