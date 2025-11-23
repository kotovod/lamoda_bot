import requests
from bs4 import BeautifulSoup
import json
import time
from typing import List, Dict

class LamodaParser:
    def __init__(self):
        self.base_url = "https://www.lamoda.ru"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.lamoda.ru/'
        }
    
    def get_products(self, url: str) -> List[Dict]:
        """
        Получает список товаров со страницы Lamoda
        
        Args:
            url: URL страницы с товарами
            
        Returns:
            Список словарей с информацией о товарах
        """
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Ищем данные в тегах script (Lamoda часто использует JSON в скриптах)
            products = []
            
            # Пытаемся найти данные в JSON внутри страницы
            scripts = soup.find_all('script', type='application/ld+json')
            
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get('@type') == 'ItemList':
                        items = data.get('itemListElement', [])
                        for item in items:
                            product_info = item.get('item', {})
                            products.append({
                                'name': product_info.get('name', 'N/A'),
                                'url': product_info.get('url', 'N/A'),
                                'image': product_info.get('image', 'N/A'),
                                'price': product_info.get('offers', {}).get('price', 'N/A'),
                                'currency': product_info.get('offers', {}).get('priceCurrency', 'RUB'),
                                'brand': product_info.get('brand', {}).get('name', 'N/A')
                            })
                except json.JSONDecodeError:
                    continue
            
            # Если не нашли в JSON, пытаемся парсить HTML
            if not products:
                products = self._parse_html_products(soup)
            
            return products
            
        except requests.RequestException as e:
            print(f"Ошибка при запросе: {e}")
            return []
    
    def _parse_html_products(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Парсит товары из HTML структуры страницы
        
        Args:
            soup: BeautifulSoup объект страницы
            
        Returns:
            Список товаров
        """
        products = []
        
        # Ищем карточки товаров (структура может меняться)
        product_cards = soup.find_all('div', class_=lambda x: x and 'x-product-card' in x)
        
        if not product_cards:
            # Альтернативные селекторы
            product_cards = soup.find_all('article', class_=lambda x: x and 'product' in str(x).lower())
        
        for card in product_cards:
            try:
                # Извлекаем информацию о товаре
                name_elem = card.find('div', class_=lambda x: x and 'title' in str(x).lower())
                name = name_elem.get_text(strip=True) if name_elem else 'N/A'
                
                price_elem = card.find('span', class_=lambda x: x and 'price' in str(x).lower())
                price = price_elem.get_text(strip=True) if price_elem else 'N/A'
                
                link_elem = card.find('a', href=True)
                url = self.base_url + link_elem['href'] if link_elem else 'N/A'
                
                img_elem = card.find('img', src=True)
                image = img_elem['src'] if img_elem else 'N/A'
                
                products.append({
                    'name': name,
                    'price': price,
                    'url': url,
                    'image': image
                })
            except Exception as e:
                print(f"Ошибка при парсинге карточки: {e}")
                continue
        
        return products
    
    def print_products(self, products: List[Dict]):
        """
        Выводит список товаров в консоль
        
        Args:
            products: Список товаров
        """
        if not products:
            print("Товары не найдены")
            return
        
        print(f"\nНайдено товаров: {len(products)}\n")
        print("=" * 80)
        
        for i, product in enumerate(products, 1):
            print(f"\n{i}. {product.get('name', 'N/A')}")
            print(f"   Цена: {product.get('price', 'N/A')} {product.get('currency', '')}")
            print(f"   URL: {product.get('url', 'N/A')}")
            if product.get('brand'):
                print(f"   Бренд: {product.get('brand')}")
            print("-" * 80)
    
    def save_to_json(self, products: List[Dict], filename: str = 'products.json'):
        """
        Сохраняет товары в JSON файл
        
        Args:
            products: Список товаров
            filename: Имя файла для сохранения
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            print(f"\nДанные сохранены в {filename}")
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")


def main():
    # URL страницы с товарами
    url = "https://www.lamoda.ru/b/1163/brand-adidasoriginals/?sort=new"
    
    # Создаем парсер
    parser = LamodaParser()
    
    print(f"Получаем данные с {url}...")
    
    # Получаем товары
    products = parser.get_products(url)
    
    # Выводим товары
    parser.print_products(products)
    
    # Сохраняем в JSON (опционально)
    if products:
        parser.save_to_json(products, 'lamoda_products.json')


if __name__ == "__main__":
    main()

