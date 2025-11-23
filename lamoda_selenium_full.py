#!/usr/bin/env python3
"""
Полный парсер Lamoda с использованием Selenium
Прокручивает страницу и получает ВСЕ товары
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import time
from typing import List, Dict
import re


class LamodaFullParser:
    def __init__(self, headless: bool = False):
        """Инициализация с Selenium"""
        self.options = Options()
        if headless:
            self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        self.driver = None
    
    def __enter__(self):
        try:
            self.driver = webdriver.Chrome(options=self.options)
            return self
        except Exception as e:
            print(f"❌ Ошибка запуска Chrome: {e}")
            print("\n💡 Для работы нужен Chrome и ChromeDriver:")
            print("   brew install --cask google-chrome")
            print("   brew install chromedriver")
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            self.driver.quit()
    
    def scroll_and_load_all(self, url: str, max_scrolls: int = 100) -> List[Dict]:
        """Прокручивает страницу и загружает все товары"""
        
        print(f"🌐 Открываем страницу: {url}")
        self.driver.get(url)
        time.sleep(3)
        
        print("📜 Начинаем прокрутку страницы...\n")
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        products_found = set()
        scroll_count = 0
        no_new_products_count = 0
        
        while scroll_count < max_scrolls:
            # Прокручиваем вниз
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)
            
            # Получаем товары на странице
            current_products = self._extract_products_from_page()
            
            new_products_count = 0
            for product in current_products:
                sku = product.get('sku')
                if sku and sku not in products_found:
                    products_found.add(sku)
                    new_products_count += 1
            
            scroll_count += 1
            
            if new_products_count > 0:
                print(f"  Прокрутка {scroll_count:2d}: найдено {len(products_found):4d} товаров (+{new_products_count} новых)")
                no_new_products_count = 0
            else:
                no_new_products_count += 1
                print(f"  Прокрутка {scroll_count:2d}: найдено {len(products_found):4d} товаров (новых нет)")
            
            # Проверяем новую высоту
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # Если высота не изменилась и нет новых товаров 3 раза подряд - конец
            if new_height == last_height and no_new_products_count >= 3:
                print("\n✅ Достигнут конец страницы")
                break
            
            last_height = new_height
        
        # Финальная выборка всех товаров
        print("\n📦 Собираем финальный список товаров...")
        all_products = self._extract_products_from_page()
        
        # Фильтруем валидные
        valid_products = [
            p for p in all_products 
            if p.get('name') and 
            p.get('name') not in ['adidas Originals', 'price'] and
            p.get('sku')
        ]
        
        # Удаляем дубликаты по SKU
        seen_skus = set()
        unique_products = []
        for product in valid_products:
            sku = product.get('sku')
            if sku and sku not in seen_skus:
                seen_skus.add(sku)
                unique_products.append(product)
        
        return unique_products
    
    def _extract_products_from_page(self) -> List[Dict]:
        """Извлекает товары с текущей страницы"""
        products = []
        
        # Получаем HTML
        html = self.driver.page_source
        
        # Ищем в скриптах
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
        
        for script in scripts:
            if 'sku' in script or 'brand' in script:
                # Ищем JSON объекты с товарами
                matches = re.findall(r'\{[^{}]*"sku"[^{}]*\}', script)
                for match in matches:
                    try:
                        data = json.loads(match)
                        if data.get('sku'):
                            products.append(data)
                    except:
                        continue
        
        return products


def print_products_summary(products: List[Dict]):
    """Выводит сводку"""
    print("\n" + "="*80)
    print(f"📦 ИТОГО ПОЛУЧЕНО УНИКАЛЬНЫХ ТОВАРОВ: {len(products)}")
    print("="*80 + "\n")
    
    # Примеры товаров
    print("ПРИМЕРЫ ТОВАРОВ:\n")
    for i, product in enumerate(products[:15], 1):
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
    
    if len(products) > 15:
        print(f"  ... и ещё {len(products) - 15} товаров\n")


def save_to_json(products: List[Dict], filename: str):
    """Сохраняет в JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"✅ Данные сохранены в {filename}")


def main():
    url = "https://www.lamoda.ru/b/1163/brand-adidasoriginals/?sort=new"
    
    print("="*80)
    print("LAMODA FULL PARSER - Selenium версия")
    print("="*80)
    print("\n🎯 Получение ВСЕХ товаров с прокруткой страницы")
    print("⚠️  Требуется установленный Chrome и ChromeDriver\n")
    print("="*80 + "\n")
    
    try:
        with LamodaFullParser(headless=False) as parser:
            products = parser.scroll_and_load_all(url, max_scrolls=50)
            
            if products:
                print_products_summary(products)
                save_to_json(products, 'lamoda_all_products_selenium.json')
                
                print("\n" + "="*80)
                print(f"✅ УСПЕШНО! Получено {len(products)} товаров")
                print("="*80 + "\n")
            else:
                print("\n❌ Товары не найдены")
    
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        print("\n" + "="*80)
        print("АЛЬТЕРНАТИВНОЕ РЕШЕНИЕ:")
        print("="*80)
        print("""
К сожалению, получить ВСЕ 1592 товара без браузера сложно, т.к.:

1. Сайт использует динамическую подгрузку (JavaScript)
2. Товары загружаются только при прокрутке
3. Нет публичного API с пагинацией

ВАРИАНТЫ:
  
  1. Использовать Selenium (требует Chrome):
     brew install --cask google-chrome
     brew install chromedriver
     python lamoda_selenium_full.py
  
  2. Использовать специализированные сервисы парсинга
     (ScrapingBee, Apify, Octoparse)
  
  3. Анализировать сетевые запросы в браузере и эмулировать API
  
Текущий скрипт получает ~50-100 товаров с первой загрузки страницы.
Это ограничение самого сайта.
""")


if __name__ == "__main__":
    main()

