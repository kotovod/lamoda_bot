import requests
from bs4 import BeautifulSoup
import json
import re
from typing import List, Dict


class LamodaAdvancedParser:
    """
    Продвинутый парсер для Lamoda - извлекает данные из JavaScript
    """
    
    def __init__(self):
        self.base_url = "https://www.lamoda.ru"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def get_products(self, url: str) -> List[Dict]:
        """
        Получает товары со страницы, извлекая JSON из JavaScript
        
        Args:
            url: URL страницы с товарами
            
        Returns:
            Список товаров
        """
        try:
            print(f"Загрузка страницы: {url}")
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Метод 1: Поиск данных в тегах script с JSON
            products = self._extract_from_scripts(soup)
            
            if not products:
                print("⚠ JSON данные не найдены, пробуем альтернативный метод...")
                # Метод 2: Извлечение из window.__NUXT__ или подобных
                products = self._extract_from_window_data(response.text)
            
            if not products:
                print("⚠ Пробуем извлечь из HTML...")
                products = self._extract_from_html(soup)
            
            return products
            
        except requests.RequestException as e:
            print(f"✗ Ошибка при запросе: {e}")
            return []
        except Exception as e:
            print(f"✗ Неожиданная ошибка: {e}")
            return []
    
    def _extract_from_scripts(self, soup: BeautifulSoup) -> List[Dict]:
        """Извлекает данные из script тегов с JSON"""
        products = []
        
        # Ищем все script теги
        scripts = soup.find_all('script', type='application/ld+json')
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                
                # Проверяем разные форматы данных
                if isinstance(data, dict):
                    # Формат ItemList
                    if data.get('@type') == 'ItemList':
                        items = data.get('itemListElement', [])
                        for item in items:
                            product_data = item.get('item', {})
                            offers = product_data.get('offers', {})
                            
                            product = {
                                'name': product_data.get('name', 'N/A'),
                                'brand': product_data.get('brand', {}).get('name', 'N/A') if isinstance(product_data.get('brand'), dict) else product_data.get('brand', 'N/A'),
                                'sku': product_data.get('sku', 'N/A'),
                                'price': offers.get('price', 'N/A'),
                                'currency': offers.get('priceCurrency', 'RUB'),
                                'url': product_data.get('url', 'N/A'),
                                'image': product_data.get('image', 'N/A'),
                                'category': product_data.get('category', 'N/A')
                            }
                            products.append(product)
                    
                    # Формат Product
                    elif data.get('@type') == 'Product':
                        offers = data.get('offers', {})
                        product = {
                            'name': data.get('name', 'N/A'),
                            'brand': data.get('brand', {}).get('name', 'N/A') if isinstance(data.get('brand'), dict) else data.get('brand', 'N/A'),
                            'sku': data.get('sku', 'N/A'),
                            'price': offers.get('price', 'N/A'),
                            'currency': offers.get('priceCurrency', 'RUB'),
                            'url': data.get('url', 'N/A'),
                            'image': data.get('image', ['N/A'])[0] if isinstance(data.get('image'), list) else data.get('image', 'N/A'),
                            'category': data.get('category', 'N/A')
                        }
                        products.append(product)
                        
            except (json.JSONDecodeError, AttributeError, KeyError) as e:
                continue
        
        return products
    
    def _extract_from_window_data(self, html: str) -> List[Dict]:
        """Извлекает данные из window.__NUXT__ или аналогичных переменных"""
        products = []
        
        try:
            # Ищем паттерны типа window.__NUXT__=...
            patterns = [
                r'window\.__NUXT__\s*=\s*({.+?});',
                r'window\.__INITIAL_STATE__\s*=\s*({.+?});',
                r'window\.__APOLLO_STATE__\s*=\s*({.+?});',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html, re.DOTALL)
                for match in matches:
                    try:
                        data = json.loads(match)
                        # Пробуем найти товары в разных местах JSON
                        products = self._find_products_in_json(data)
                        if products:
                            return products
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            print(f"Ошибка при извлечении из window data: {e}")
        
        return products
    
    def _find_products_in_json(self, data: dict, depth: int = 0) -> List[Dict]:
        """Рекурсивно ищет товары в JSON структуре"""
        products = []
        
        if depth > 5:  # Ограничиваем глубину рекурсии
            return products
        
        if isinstance(data, dict):
            # Проверяем, является ли это товаром
            if 'name' in data and ('price' in data or 'sku' in data):
                product = {
                    'name': data.get('name', 'N/A'),
                    'brand': data.get('brand', 'N/A'),
                    'sku': data.get('sku', 'N/A'),
                    'price': data.get('price', 'N/A'),
                    'url': data.get('url', 'N/A'),
                    'image': data.get('image', 'N/A')
                }
                return [product]
            
            # Ищем в подобъектах
            for key, value in data.items():
                if key in ['products', 'items', 'data', 'catalog']:
                    if isinstance(value, list):
                        for item in value:
                            found = self._find_products_in_json(item, depth + 1)
                            products.extend(found)
                    elif isinstance(value, dict):
                        found = self._find_products_in_json(value, depth + 1)
                        products.extend(found)
        
        elif isinstance(data, list):
            for item in data:
                found = self._find_products_in_json(item, depth + 1)
                products.extend(found)
        
        return products
    
    def _extract_from_html(self, soup: BeautifulSoup) -> List[Dict]:
        """Извлекает данные напрямую из HTML (менее надежный метод)"""
        products = []
        
        # Различные возможные селекторы для карточек товаров
        card_selectors = [
            {'name': 'div', 'class_': 'x-product-card'},
            {'name': 'div', 'attrs': {'data-item': True}},
            {'name': 'article', 'class_': lambda x: x and 'product' in str(x).lower()},
        ]
        
        product_cards = []
        for selector in card_selectors:
            product_cards = soup.find_all(**selector)
            if product_cards:
                print(f"✓ Найдено {len(product_cards)} карточек товаров")
                break
        
        if not product_cards:
            return []
        
        for card in product_cards:
            try:
                # Название
                name_elem = (
                    card.find(attrs={'itemprop': 'name'}) or
                    card.find(class_=re.compile(r'title|name|product-title', re.I)) or
                    card.find('div', class_=lambda x: x and 'title' in str(x).lower())
                )
                name = name_elem.get_text(strip=True) if name_elem else 'N/A'
                
                # Бренд
                brand_elem = (
                    card.find(attrs={'itemprop': 'brand'}) or
                    card.find(class_=re.compile(r'brand', re.I))
                )
                brand = brand_elem.get_text(strip=True) if brand_elem else 'N/A'
                
                # Цена
                price_elem = (
                    card.find(attrs={'itemprop': 'price'}) or
                    card.find(class_=re.compile(r'price|cost', re.I)) or
                    card.find('span', class_=lambda x: x and 'price' in str(x).lower())
                )
                price = price_elem.get_text(strip=True) if price_elem else 'N/A'
                
                # URL
                link_elem = card.find('a', href=True)
                url = self.base_url + link_elem['href'] if link_elem and not link_elem['href'].startswith('http') else link_elem['href'] if link_elem else 'N/A'
                
                # Изображение
                img_elem = card.find('img')
                image = img_elem.get('src') or img_elem.get('data-src') if img_elem else 'N/A'
                
                # SKU (артикул) из URL
                sku = 'N/A'
                if link_elem and 'href' in link_elem.attrs:
                    match = re.search(r'/p/([^/]+)/', link_elem['href'])
                    if match:
                        sku = match.group(1)
                
                product = {
                    'name': name,
                    'brand': brand,
                    'sku': sku,
                    'price': price,
                    'url': url,
                    'image': image
                }
                
                products.append(product)
                
            except Exception as e:
                continue
        
        return products
    
    def print_products(self, products: List[Dict], limit: int = None):
        """Выводит товары в консоль"""
        if not products:
            print("\n⚠ Товары не найдены")
            return
        
        display_products = products[:limit] if limit else products
        
        print(f"\n{'='*80}")
        print(f"✓ Всего найдено товаров: {len(products)}")
        if limit and len(products) > limit:
            print(f"  Показано первых: {limit}")
        print(f"{'='*80}\n")
        
        for i, product in enumerate(display_products, 1):
            print(f"{i}. {product.get('name', 'N/A')}")
            if product.get('brand', 'N/A') != 'N/A':
                print(f"   Бренд: {product['brand']}")
            if product.get('sku', 'N/A') != 'N/A':
                print(f"   Артикул: {product['sku']}")
            print(f"   Цена: {product.get('price', 'N/A')} {product.get('currency', '')}")
            print(f"   URL: {product.get('url', 'N/A')}")
            print(f"{'-'*80}\n")
    
    def save_to_json(self, products: List[Dict], filename: str = 'lamoda_products_advanced.json'):
        """Сохраняет товары в JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            print(f"✓ Данные сохранены в {filename}")
            print(f"  Всего товаров: {len(products)}")
        except Exception as e:
            print(f"✗ Ошибка при сохранении: {e}")


def main():
    url = "https://www.lamoda.ru/b/1163/brand-adidasoriginals/?sort=new"
    
    print("="*80)
    print("Lamoda Advanced Parser - Извлечение данных из JavaScript")
    print("="*80)
    print()
    
    parser = LamodaAdvancedParser()
    products = parser.get_products(url)
    
    # Выводим первые 30 товаров
    parser.print_products(products, limit=30)
    
    # Сохраняем все товары
    if products:
        parser.save_to_json(products)
    else:
        print("\n⚠ Товары не найдены. Рекомендации:")
        print("  1. Попробуйте версию с Selenium: lamoda_parser_selenium.py")
        print("  2. Сайт может использовать защиту от ботов")
        print("  3. Может потребоваться капча или авторизация")


if __name__ == "__main__":
    main()

