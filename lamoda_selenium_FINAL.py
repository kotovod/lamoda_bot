#!/usr/bin/env python3
"""
Финальная рабочая версия с Selenium - извлекает ВСЕ товары
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json
import time
from typing import List, Dict


class LamodaFinalSelenium:
    def __init__(self, headless: bool = False):
        self.options = Options()
        if headless:
            self.options.add_argument('--headless=new')
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
    
    def get_all_products(self, url: str) -> List[Dict]:
        """Получает все товары"""
        
        print(f"🌐 Открываем: {url}")
        self.driver.get(url)
        time.sleep(5)
        
        print("📜 Прокручиваем для загрузки всех товаров...\n")
        
        last_count = 0
        no_change = 0
        
        for scroll in range(100):  # Увеличили до 100 прокруток
            # Прокрутка
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Увеличили задержку до 2 секунд
            
            # Ищем элементы по разным селекторам
            count = 0
            selectors_to_try = [
                "article",
                "[class*='ProductCard']",
                "[class*='product']",
                ".x-product-card__link",
                "a[href*='/p/RT']"
            ]
            
            for selector in selectors_to_try:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(elements) > count:
                        count = len(elements)
                except:
                    continue
            
            if count > last_count:
                print(f"  Прокрутка {scroll+1:2d}: {count:4d} элементов (+{count-last_count})")
                last_count = count
                no_change = 0
            else:
                no_change += 1
                if no_change % 3 == 0:
                    print(f"  Прокрутка {scroll+1:2d}: {count:4d} элементов (без изменений)")
            
            if no_change >= 10:  # Увеличили до 10 прокруток без изменений
                print("\n✅ Загрузка завершена")
                break
        
        print(f"\n📦 Извлекаем данные из {last_count} элементов...")
        
        # Извлекаем товары
        products = []
        
        # Ищем все ссылки на товары (изменен селектор!)
        try:
            links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/']")
            print(f"  Найдено ссылок на товары: {len(links)}")
            
            seen_skus = set()
            for link in links:
                try:
                    href = link.get_attribute('href')
                    if href and '/p/' in href:
                        # Извлекаем SKU из URL
                        sku_raw = href.split('/p/')[1].split('/')[0].split('?')[0]
                        sku = sku_raw.upper()  # Приводим к верхнему регистру
                        
                        if sku and sku not in seen_skus and sku.startswith('RTL'):
                            seen_skus.add(sku)
                            
                            # Пытаемся получить название
                            try:
                                # Ищем родительский элемент и текст
                                parent = link
                                for _ in range(3):  # Поднимаемся до 3 уровней вверх
                                    try:
                                        parent = parent.find_element(By.XPATH, '..')
                                        text = parent.text
                                        if text and len(text) > 3:
                                            name = text.split('\n')[0]
                                            break
                                    except:
                                        continue
                                else:
                                    name = link.text or 'N/A'
                            except:
                                name = 'N/A'
                            
                            products.append({
                                'sku': sku,
                                'name': name[:100] if name else 'N/A',  # Ограничиваем длину
                                'url': f"https://www.lamoda.ru/p/{sku}/"
                            })
                except Exception as e:
                    continue
        
        except Exception as e:
            print(f"  Ошибка: {e}")
        
        print(f"  ✅ Извлечено уникальных товаров: {len(products)}")
        
        return products


def main():
    url = "https://www.lamoda.ru/b/1163/brand-adidasoriginals/?sort=new"
    
    print("="*80)
    print("LAMODA PARSER - ФИНАЛЬНАЯ ВЕРСИЯ (ВСЕ ТОВАРЫ)")
    print("="*80 + "\n")
    
    try:
        with LamodaFinalSelenium(headless=False) as parser:
            products = parser.get_all_products(url)
            
            print("\n" + "="*80)
            print(f"🎉 УСПЕШНО ПОЛУЧЕНО: {len(products)} ТОВАРОВ")
            print("="*80 + "\n")
            
            if products:
                # Статистика
                categories = {'Обувь': 0, 'Одежда': 0, 'Аксессуары': 0, 'Другое': 0}
                for p in products:
                    name = p.get('name', '').lower()
                    if any(w in name for w in ['кед', 'кроссов', 'сланц', 'сабо']):
                        categories['Обувь'] += 1
                    elif any(w in name for w in ['футбол', 'худи', 'брюки', 'куртк']):
                        categories['Одежда'] += 1
                    elif any(w in name for w in ['носки', 'шапк']):
                        categories['Аксессуары'] += 1
                    else:
                        categories['Другое'] += 1
                
                print("📊 СТАТИСТИКА:\n")
                for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                    if count > 0:
                        bar = '█' * (count // 50)
                        print(f"  {cat:15s}: {bar} {count}")
                
                # Примеры
                print("\n" + "="*80)
                print("ПРИМЕРЫ ТОВАРОВ (первые 20):\n")
                for i, p in enumerate(products[:20], 1):
                    print(f"  {i:2d}. {p.get('name', 'N/A')}")
                    print(f"      Артикул: {p.get('sku')}")
                    print()
                
                if len(products) > 20:
                    print(f"  ... и ещё {len(products) - 20} товаров\n")
                
                # Сохраняем
                with open('lamoda_all_products_FINAL.json', 'w', encoding='utf-8') as f:
                    json.dump(products, f, ensure_ascii=False, indent=2)
                print("="*80)
                print("✅ Данные сохранены в: lamoda_all_products_FINAL.json")
                print("="*80 + "\n")
            else:
                print("⚠️ Товары не найдены\n")
    
    except Exception as e:
        print(f"\n❌ Ошибка: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

