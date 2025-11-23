#!/usr/bin/env python3
"""
Улучшенный Selenium парсер - ищет товары через DOM элементы
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json
import time
from typing import List, Dict


class LamodaSeleniumImproved:
    def __init__(self, headless: bool = False):
        self.options = Options()
        if headless:
            self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        self.driver = None
    
    def __enter__(self):
        self.driver = webdriver.Chrome(options=self.options)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            self.driver.quit()
    
    def get_all_products(self, url: str, max_scrolls: int = 50) -> List[Dict]:
        """Получает все товары с прокруткой"""
        
        print(f"🌐 Открываем: {url}")
        self.driver.get(url)
        time.sleep(5)  # Даем время загрузиться
        
        print("📜 Прокручиваем страницу...\n")
        
        last_product_count = 0
        no_change_count = 0
        
        for scroll in range(max_scrolls):
            # Прокрутка
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Считаем товары на странице (ищем data-item-id или подобные атрибуты)
            try:
                # Пытаемся найти карточки товаров по разным селекторам
                product_cards = []
                
                selectors = [
                    "[data-item-id]",
                    ".x-product-card",
                    "[class*='ProductCard']",
                    "[class*='product-card']",
                    "article"
                ]
                
                for selector in selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            product_cards = elements
                            break
                    except:
                        continue
                
                current_count = len(product_cards)
                
                if current_count > last_product_count:
                    new_items = current_count - last_product_count
                    print(f"  Прокрутка {scroll+1:2d}: {current_count:4d} товаров (+{new_items} новых)")
                    last_product_count = current_count
                    no_change_count = 0
                else:
                    no_change_count += 1
                    print(f"  Прокрутка {scroll+1:2d}: {current_count:4d} товаров (новых нет)")
                
                # Если 5 прокруток подряд без изменений - конец
                if no_change_count >= 5:
                    print("\n✅ Больше товаров не загружается")
                    break
                    
            except Exception as e:
                print(f"  Ошибка: {e}")
                continue
        
        # Собираем финальные данные
        print(f"\n📦 Собираем данные о {last_product_count} товарах...")
        products = self._extract_all_products()
        
        return products
    
    def _extract_all_products(self) -> List[Dict]:
        """Извлекает все товары со страницы"""
        products = []
        
        # Метод 1: Ищем в page_source
        page_source = self.driver.page_source
        
        # Ищем JSON с товарами в window.__NUXT__, __INITIAL_STATE__ и т.д.
        import re
        
        # Паттерны для поиска данных
        patterns = [
            (r'window\.__NUXT__\s*=\s*(\{.+?\});', 'NUXT'),
            (r'window\.__INITIAL_STATE__\s*=\s*(\{.+?\});', 'INITIAL_STATE'),
            (r'"products"\s*:\s*(\[.+?\])', 'products array'),
        ]
        
        for pattern, name in patterns:
            matches = re.search(pattern, page_source, re.DOTALL)
            if matches:
                try:
                    data_str = matches.group(1)
                    # Ограничиваем размер для безопасности
                    if len(data_str) < 10000000:  # 10MB max
                        data = json.loads(data_str)
                        found_products = self._find_products_in_data(data)
                        if found_products:
                            print(f"  ✅ Найдено в {name}: {len(found_products)} товаров")
                            products.extend(found_products)
                except Exception as e:
                    print(f"  ⚠️ Ошибка парсинга {name}: {e}")
                    continue
        
        # Метод 2: Извлекаем из DOM элементов
        try:
            product_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-item-id]")
            print(f"  ✅ Найдено элементов с data-item-id: {len(product_elements)}")
            
            for elem in product_elements:
                try:
                    product = {
                        'sku': elem.get_attribute('data-item-id'),
                        'name': elem.text.split('\n')[0] if elem.text else 'N/A',
                    }
                    if product['sku']:
                        products.append(product)
                except:
                    continue
        except Exception as e:
            print(f"  ⚠️ Ошибка извлечения из DOM: {e}")
        
        # Удаляем дубликаты
        seen = set()
        unique_products = []
        for p in products:
            sku = p.get('sku')
            if sku and sku not in seen:
                seen.add(sku)
                unique_products.append(p)
        
        return unique_products
    
    def _find_products_in_data(self, data, depth=0):
        """Рекурсивно ищет товары в JSON"""
        if depth > 10:
            return []
        
        products = []
        
        if isinstance(data, dict):
            # Проверяем, это товар?
            if 'sku' in data and data.get('sku'):
                return [data]
            
            # Ищем в ключах products, items, data
            for key in ['products', 'items', 'data', 'catalog']:
                if key in data:
                    found = self._find_products_in_data(data[key], depth + 1)
                    products.extend(found)
            
            # Ищем во всех значениях
            for value in data.values():
                if isinstance(value, (dict, list)):
                    found = self._find_products_in_data(value, depth + 1)
                    products.extend(found)
        
        elif isinstance(data, list):
            for item in data:
                found = self._find_products_in_data(item, depth + 1)
                products.extend(found)
        
        return products


def main():
    url = "https://www.lamoda.ru/b/1163/brand-adidasoriginals/?sort=new"
    
    print("="*80)
    print("LAMODA SELENIUM PARSER - Улучшенная версия")
    print("="*80 + "\n")
    
    try:
        with LamodaSeleniumImproved(headless=False) as parser:
            products = parser.get_all_products(url, max_scrolls=50)
            
            print("\n" + "="*80)
            print(f"✅ ИТОГО ПОЛУЧЕНО: {len(products)} товаров")
            print("="*80 + "\n")
            
            if products:
                # Показываем примеры
                print("ПРИМЕРЫ ТОВАРОВ:\n")
                for i, p in enumerate(products[:20], 1):
                    print(f"  {i:2d}. {p.get('name', 'N/A')}")
                    print(f"      Артикул: {p.get('sku', 'N/A')}")
                    print()
                
                if len(products) > 20:
                    print(f"  ... и ещё {len(products) - 20} товаров\n")
                
                # Сохраняем
                with open('lamoda_all_selenium.json', 'w', encoding='utf-8') as f:
                    json.dump(products, f, ensure_ascii=False, indent=2)
                print(f"✅ Сохранено в lamoda_all_selenium.json\n")
            else:
                print("⚠️ Товары не найдены\n")
    
    except Exception as e:
        print(f"\n❌ Ошибка: {e}\n")


if __name__ == "__main__":
    main()

