from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import time
from typing import List, Dict


class LamodaSeleniumParser:
    def __init__(self, headless: bool = True):
        """
        Инициализация парсера с использованием Selenium
        
        Args:
            headless: Запускать браузер в фоновом режиме
        """
        self.options = Options()
        if headless:
            self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        self.driver = None
    
    def __enter__(self):
        self.driver = webdriver.Chrome(options=self.options)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            self.driver.quit()
    
    def get_products(self, url: str, wait_time: int = 10) -> List[Dict]:
        """
        Получает список товаров со страницы
        
        Args:
            url: URL страницы
            wait_time: Время ожидания загрузки элементов
            
        Returns:
            Список товаров
        """
        if not self.driver:
            raise RuntimeError("Драйвер не инициализирован. Используйте context manager.")
        
        try:
            print(f"Открываем страницу: {url}")
            self.driver.get(url)
            
            # Ждем загрузки товаров
            print("Ожидание загрузки товаров...")
            time.sleep(3)  # Даем время для начальной загрузки
            
            # Прокручиваем страницу для загрузки товаров
            self._scroll_page()
            
            products = []
            
            # Пытаемся найти карточки товаров по разным селекторам
            selectors = [
                (By.CLASS_NAME, "x-product-card"),
                (By.CSS_SELECTOR, "[data-item-id]"),
                (By.CSS_SELECTOR, "div[class*='product-card']"),
                (By.CSS_SELECTOR, "article[class*='product']"),
            ]
            
            product_elements = []
            for by, selector in selectors:
                try:
                    product_elements = self.driver.find_elements(by, selector)
                    if product_elements:
                        print(f"Найдено элементов: {len(product_elements)} (селектор: {selector})")
                        break
                except NoSuchElementException:
                    continue
            
            if not product_elements:
                print("Не удалось найти элементы товаров. Попробуем извлечь из JSON данных...")
                return self._extract_from_page_data()
            
            # Парсим каждую карточку товара
            for element in product_elements:
                try:
                    product = self._parse_product_element(element)
                    if product:
                        products.append(product)
                except Exception as e:
                    print(f"Ошибка при парсинге элемента: {e}")
                    continue
            
            return products
            
        except Exception as e:
            print(f"Ошибка при получении товаров: {e}")
            return []
    
    def _scroll_page(self, scrolls: int = 3):
        """Прокручивает страницу для загрузки динамического контента"""
        for i in range(scrolls):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
    
    def _parse_product_element(self, element) -> Dict:
        """
        Извлекает информацию о товаре из элемента
        
        Args:
            element: WebElement карточки товара
            
        Returns:
            Словарь с данными товара
        """
        product = {}
        
        try:
            # Название
            try:
                name_elem = element.find_element(By.CSS_SELECTOR, "[class*='title'], [class*='name'], [itemprop='name']")
                product['name'] = name_elem.text.strip()
            except NoSuchElementException:
                product['name'] = 'N/A'
            
            # Цена
            try:
                price_elem = element.find_element(By.CSS_SELECTOR, "[class*='price'], [itemprop='price']")
                product['price'] = price_elem.text.strip()
            except NoSuchElementException:
                product['price'] = 'N/A'
            
            # URL
            try:
                link_elem = element.find_element(By.TAG_NAME, 'a')
                product['url'] = link_elem.get_attribute('href')
            except NoSuchElementException:
                product['url'] = 'N/A'
            
            # Изображение
            try:
                img_elem = element.find_element(By.TAG_NAME, 'img')
                product['image'] = img_elem.get_attribute('src') or img_elem.get_attribute('data-src')
            except NoSuchElementException:
                product['image'] = 'N/A'
            
            # Бренд
            try:
                brand_elem = element.find_element(By.CSS_SELECTOR, "[class*='brand'], [itemprop='brand']")
                product['brand'] = brand_elem.text.strip()
            except NoSuchElementException:
                product['brand'] = 'N/A'
            
            return product if product.get('name') != 'N/A' else None
            
        except Exception as e:
            print(f"Ошибка при извлечении данных: {e}")
            return None
    
    def _extract_from_page_data(self) -> List[Dict]:
        """
        Пытается извлечь данные из JSON в коде страницы
        
        Returns:
            Список товаров
        """
        try:
            # Получаем весь HTML
            page_source = self.driver.page_source
            
            # Ищем JSON данные (часто они находятся в window.__INITIAL_STATE__ или подобных переменных)
            scripts = self.driver.find_elements(By.TAG_NAME, 'script')
            
            for script in scripts:
                script_content = script.get_attribute('innerHTML')
                if script_content and ('products' in script_content.lower() or 'items' in script_content.lower()):
                    # Здесь можно добавить более сложную логику извлечения JSON
                    print("Найден потенциальный JSON со товарами в скрипте")
                    # TODO: Извлечь и распарсить JSON
                    
            return []
        except Exception as e:
            print(f"Ошибка при извлечении из JSON: {e}")
            return []
    
    def print_products(self, products: List[Dict]):
        """Выводит список товаров"""
        if not products:
            print("Товары не найдены")
            return
        
        print(f"\nНайдено товаров: {len(products)}\n")
        print("=" * 80)
        
        for i, product in enumerate(products, 1):
            print(f"\n{i}. {product.get('name', 'N/A')}")
            print(f"   Цена: {product.get('price', 'N/A')}")
            print(f"   Бренд: {product.get('brand', 'N/A')}")
            print(f"   URL: {product.get('url', 'N/A')}")
            print("-" * 80)
    
    def save_to_json(self, products: List[Dict], filename: str = 'products.json'):
        """Сохраняет товары в JSON файл"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            print(f"\nДанные сохранены в {filename}")
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")


def main():
    url = "https://www.lamoda.ru/b/1163/brand-adidasoriginals/?sort=new"
    
    print("Запуск парсера с использованием Selenium...")
    print("Это может занять некоторое время...\n")
    
    with LamodaSeleniumParser(headless=False) as parser:
        products = parser.get_products(url)
        parser.print_products(products)
        
        if products:
            parser.save_to_json(products, 'lamoda_products_selenium.json')


if __name__ == "__main__":
    main()

