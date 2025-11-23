#!/usr/bin/env python3
"""
Отладочная версия - сохраняет HTML для анализа
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time


def save_page_html():
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('user-agent=Mozilla/5.0')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        url = "https://www.lamoda.ru/b/1163/brand-adidasoriginals/?sort=new"
        print(f"Загружаем: {url}")
        driver.get(url)
        time.sleep(5)
        
        # Прокручиваем немного
        for i in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        # Сохраняем HTML
        html = driver.page_source
        with open('lamoda_selenium_page.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ HTML сохранен в lamoda_selenium_page.html ({len(html)} байт)")
        
        # Пробуем разные селекторы
        print("\n📊 Тестируем селекторы:")
        
        selectors = [
            ("a[href*='/p/']", "Ссылки с /p/"),
            ("a[href*='RT']", "Ссылки с RT"),
            ("a", "Все ссылки"),
            ("[class*='product']", "Элементы с 'product'"),
            ("[class*='Product']", "Элементы с 'Product'"),
            ("article", "article элементы"),
            ("[data-item]", "data-item атрибуты"),
        ]
        
        for selector, desc in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"  {selector:30s} : {len(elements):4d} - {desc}")
                
                if elements and len(elements) < 10:
                    for elem in elements[:3]:
                        try:
                            print(f"    - {elem.get_attribute('href') or elem.get_attribute('class') or elem.text[:50]}")
                        except:
                            pass
            except Exception as e:
                print(f"  {selector:30s} : ERROR - {e}")
        
    finally:
        driver.quit()


if __name__ == "__main__":
    save_page_html()

