import requests
import json
from typing import List, Dict
import time


class LamodaAPIParser:
    """
    Парсер для Lamoda через API (более надежный метод)
    """
    
    def __init__(self):
        self.api_url = "https://www.lamoda.ru/api/v1/catalog/products"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.lamoda.ru/',
            'x-requested-with': 'XMLHttpRequest'
        }
    
    def get_products(self, brand_id: str = "1163", page: int = 1, limit: int = 60) -> List[Dict]:
        """
        Получает товары через API
        
        Args:
            brand_id: ID бренда (1163 для adidas originals)
            page: Номер страницы
            limit: Количество товаров на странице
            
        Returns:
            Список товаров
        """
        try:
            # Параметры запроса
            params = {
                'filters[0][type]': 'multi',
                'filters[0][id]': 'brand',
                'filters[0][values][0]': brand_id,
                'sort': 'new',
                'page': page,
                'limit': limit
            }
            
            print(f"Запрос к API: страница {page}, лимит {limit}")
            response = requests.get(self.api_url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            products = []
            
            # Извлекаем товары из ответа
            if 'data' in data and 'products' in data['data']:
                for item in data['data']['products']:
                    product = {
                        'sku': item.get('sku', 'N/A'),
                        'name': item.get('name', 'N/A'),
                        'brand': item.get('brand', {}).get('name', 'N/A'),
                        'price': item.get('price', {}).get('current', {}).get('value', 'N/A'),
                        'old_price': item.get('price', {}).get('previous', {}).get('value', None),
                        'currency': item.get('price', {}).get('current', {}).get('currency', 'RUB'),
                        'url': f"https://www.lamoda.ru/p/{item.get('sku', '')}/",
                        'image': item.get('images', [{}])[0].get('large', 'N/A') if item.get('images') else 'N/A',
                        'category': item.get('category', {}).get('name', 'N/A'),
                        'rating': item.get('rating', {}).get('value', 'N/A'),
                        'reviews_count': item.get('rating', {}).get('count', 0)
                    }
                    products.append(product)
            
            return products
            
        except requests.RequestException as e:
            print(f"Ошибка при запросе к API: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"Ошибка при парсинге JSON: {e}")
            return []
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            return []
    
    def get_all_products(self, brand_id: str = "1163", max_pages: int = 10) -> List[Dict]:
        """
        Получает все товары со всех страниц
        
        Args:
            brand_id: ID бренда
            max_pages: Максимальное количество страниц для загрузки
            
        Returns:
            Список всех товаров
        """
        all_products = []
        
        for page in range(1, max_pages + 1):
            print(f"\nЗагрузка страницы {page}...")
            products = self.get_products(brand_id, page)
            
            if not products:
                print("Больше нет товаров")
                break
            
            all_products.extend(products)
            print(f"Загружено товаров: {len(products)}")
            
            # Небольшая задержка, чтобы не нагружать сервер
            time.sleep(0.5)
        
        return all_products
    
    def print_products(self, products: List[Dict], limit: int = None):
        """
        Выводит список товаров в консоль
        
        Args:
            products: Список товаров
            limit: Максимальное количество товаров для вывода
        """
        if not products:
            print("Товары не найдены")
            return
        
        display_products = products[:limit] if limit else products
        
        print(f"\n{'='*80}")
        print(f"Всего найдено товаров: {len(products)}")
        if limit and len(products) > limit:
            print(f"Показано первых: {limit}")
        print(f"{'='*80}\n")
        
        for i, product in enumerate(display_products, 1):
            print(f"{i}. {product.get('name', 'N/A')}")
            print(f"   Артикул: {product.get('sku', 'N/A')}")
            print(f"   Бренд: {product.get('brand', 'N/A')}")
            
            price = product.get('price', 'N/A')
            old_price = product.get('old_price')
            currency = product.get('currency', '')
            
            if old_price:
                print(f"   Цена: {price} {currency} (было: {old_price} {currency})")
            else:
                print(f"   Цена: {price} {currency}")
            
            print(f"   Категория: {product.get('category', 'N/A')}")
            
            rating = product.get('rating')
            if rating != 'N/A':
                print(f"   Рейтинг: {rating} ({product.get('reviews_count', 0)} отзывов)")
            
            print(f"   URL: {product.get('url', 'N/A')}")
            print(f"{'-'*80}\n")
    
    def save_to_json(self, products: List[Dict], filename: str = 'lamoda_products_api.json'):
        """
        Сохраняет товары в JSON файл
        
        Args:
            products: Список товаров
            filename: Имя файла
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            print(f"\n✓ Данные успешно сохранены в {filename}")
            print(f"  Всего товаров: {len(products)}")
        except Exception as e:
            print(f"✗ Ошибка при сохранении: {e}")


def main():
    parser = LamodaAPIParser()
    
    print("="*80)
    print("Lamoda Parser - Получение товаров через API")
    print("="*80)
    print("\nБренд: Adidas Originals")
    print("Сортировка: Новинки\n")
    
    # Получаем товары (первые 3 страницы = ~180 товаров)
    products = parser.get_all_products(brand_id="1163", max_pages=3)
    
    # Выводим первые 20 товаров
    parser.print_products(products, limit=20)
    
    # Сохраняем все в JSON
    if products:
        parser.save_to_json(products)
    else:
        print("\n⚠ Не удалось получить товары. Возможно:")
        print("  - Сайт изменил API")
        print("  - Требуется авторизация")
        print("  - Используется защита от ботов")
        print("\nПопробуйте использовать версию с Selenium: lamoda_parser_selenium.py")


if __name__ == "__main__":
    main()

