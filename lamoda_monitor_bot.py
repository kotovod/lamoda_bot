#!/usr/bin/env python3
"""
Telegram бот для мониторинга новых товаров на Lamoda
Проверяет появление новинок каждый час и отправляет уведомления
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
import logging
from datetime import datetime
from typing import List, Dict, Set
import os


# ====================== КОНФИГУРАЦИЯ ======================

TELEGRAM_BOT_TOKEN = "7926186760:AAFQ-N4S55QRh4nI0WwPxU2p4cQ1PKTLFiU"
TELEGRAM_CHAT_ID = None  # Будет определен автоматически при первом запуске

LAMODA_URL = "https://www.lamoda.ru/b/1163/brand-adidasoriginals/?sort=new"
CHECK_INTERVAL = 3600  # 1 час в секундах

KNOWN_PRODUCTS_FILE = "known_products.json"
CHAT_ID_FILE = "chat_id.json"

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lamoda_monitor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# ====================== ПАРСИНГ LAMODA ======================

def parse_lamoda_products(url: str) -> List[Dict]:
    """Парсит товары с Lamoda (проверенный метод)"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        html = response.text
        
        products = []
        
        # Метод 1: window.dataLayer
        dataLayer_match = re.search(r'window\.dataLayer\s*=\s*\[(.*?)\];', html, re.DOTALL)
        if dataLayer_match:
            try:
                dataLayer_str = '[' + dataLayer_match.group(1) + ']'
                dataLayer_str = re.sub(r"'([^']*)'", r'"\1"', dataLayer_str)
                dataLayer = json.loads(dataLayer_str)
                
                for entry in dataLayer:
                    if 'ecommerce' in entry:
                        ecom = entry['ecommerce']
                        if 'impressions' in ecom:
                            for item in ecom['impressions']:
                                products.append({
                                    'name': item.get('name'),
                                    'brand': item.get('brand'),
                                    'price': item.get('price'),
                                    'sku': item.get('id'),
                                    'url': f"https://www.lamoda.ru/p/{item.get('id')}/"
                                })
            except:
                pass
        
        # Метод 2: JSON в скриптах
        json_pattern = r'<script[^>]*>(.*?)</script>'
        scripts = re.findall(json_pattern, html, re.DOTALL)
        
        for script in scripts:
            if 'products' in script or 'items' in script:
                try:
                    json_objects = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', script)
                    for json_str in json_objects:
                        if 'sku' in json_str or 'name' in json_str:
                            try:
                                data = json.loads(json_str)
                                if isinstance(data, dict) and 'name' in data:
                                    products.append(data)
                            except:
                                continue
                except:
                    continue
        
        # Фильтруем валидные товары
        valid_products = []
        for p in products:
            if p.get('name') and p.get('name') not in ['adidas Originals', 'price'] and p.get('sku'):
                valid_products.append(p)
        
        return valid_products
        
    except Exception as e:
        logger.error(f"Ошибка при парсинге Lamoda: {e}")
        return []


# ====================== РАБОТА С ДАННЫМИ ======================

def load_known_products() -> Set[str]:
    """Загружает список известных SKU товаров"""
    if os.path.exists(KNOWN_PRODUCTS_FILE):
        try:
            with open(KNOWN_PRODUCTS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data)
        except:
            return set()
    return set()


def save_known_products(known_skus: Set[str]):
    """Сохраняет список известных SKU"""
    with open(KNOWN_PRODUCTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(known_skus), f, ensure_ascii=False, indent=2)


def load_chat_id() -> str:
    """Загружает сохраненный chat_id"""
    if os.path.exists(CHAT_ID_FILE):
        try:
            with open(CHAT_ID_FILE, 'r') as f:
                data = json.load(f)
                return data.get('chat_id')
        except:
            return None
    return None


def save_chat_id(chat_id: str):
    """Сохраняет chat_id"""
    with open(CHAT_ID_FILE, 'w') as f:
        json.dump({'chat_id': chat_id}, f)


def get_chat_id() -> str:
    """Получает chat_id автоматически"""
    
    # Пробуем загрузить сохраненный
    saved_id = load_chat_id()
    if saved_id:
        return saved_id
    
    # Получаем через getUpdates
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get('ok') and data.get('result'):
            for update in data['result']:
                if 'message' in update:
                    chat_id = update['message']['chat']['id']
                    logger.info(f"Chat ID найден: {chat_id}")
                    save_chat_id(str(chat_id))
                    return str(chat_id)
        
        logger.warning("Chat ID не найден. Отправьте любое сообщение боту.")
        return None
        
    except Exception as e:
        logger.error(f"Ошибка получения chat_id: {e}")
        return None


# ====================== TELEGRAM ======================

def get_product_image_url(sku: str) -> str:
    """Получает URL изображения товара"""
    # Пробуем получить изображение со страницы товара
    try:
        url = f"https://www.lamoda.ru/p/{sku}/"
        response = requests.get(url, timeout=10)
        
        # Ищем изображение в meta tags
        soup = BeautifulSoup(response.text, 'html.parser')
        og_image = soup.find('meta', property='og:image')
        
        if og_image and og_image.get('content'):
            return og_image['content']
        
        # Альтернативный поиск
        img_pattern = r'https://a\.lmcdn\.ru/img[^"\']*\.jpg'
        matches = re.findall(img_pattern, response.text)
        if matches:
            return matches[0]
            
    except:
        pass
    
    # Fallback - используем стандартный формат URL Lamoda
    return f"https://a.lmcdn.ru/product/{sku}/default.jpg"


def send_telegram_photo(chat_id: str, photo_url: str, caption: str) -> bool:
    """Отправляет фото с подписью в Telegram"""
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        
        data = {
            'chat_id': chat_id,
            'photo': photo_url,
            'caption': caption,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, timeout=30)
        
        if response.status_code == 200:
            return True
        else:
            logger.error(f"Ошибка отправки в Telegram: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Ошибка при отправке фото: {e}")
        return False


def send_telegram_message(chat_id: str, text: str) -> bool:
    """Отправляет текстовое сообщение"""
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
        
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}")
        return False


def notify_new_product(chat_id: str, product: Dict):
    """Отправляет уведомление о новом товаре"""
    
    name = product.get('name', 'N/A')
    price = product.get('price', 'N/A')
    sku = product.get('sku', '')
    url = product.get('url', f"https://www.lamoda.ru/p/{sku}/")
    
    # Формируем caption
    caption = f"🆕 <b>Новый товар!</b>\n\n"
    caption += f"📦 {name}\n"
    caption += f"💰 Цена: {price} ₽\n"
    caption += f"🔗 <a href='{url}'>Открыть на Lamoda</a>"
    
    # Получаем изображение
    photo_url = get_product_image_url(sku)
    
    logger.info(f"Отправляем уведомление о товаре: {name} (SKU: {sku})")
    
    # Отправляем с фото
    success = send_telegram_photo(chat_id, photo_url, caption)
    
    if success:
        logger.info(f"✅ Уведомление отправлено: {name}")
    else:
        logger.error(f"❌ Не удалось отправить уведомление: {name}")
    
    # Небольшая задержка между сообщениями
    time.sleep(1)


# ====================== ОСНОВНАЯ ЛОГИКА ======================

def check_for_new_products(chat_id: str):
    """Проверяет появление новых товаров"""
    
    logger.info("="*60)
    logger.info(f"🔍 Проверка новых товаров: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Загружаем известные товары
    known_skus = load_known_products()
    logger.info(f"📊 Известных товаров: {len(known_skus)}")
    
    # Парсим текущие товары
    current_products = parse_lamoda_products(LAMODA_URL)
    logger.info(f"📦 Получено товаров: {len(current_products)}")
    
    if not current_products:
        logger.warning("⚠️  Не удалось получить товары")
        return
    
    # Находим новые товары
    new_products = []
    current_skus = set()
    
    for product in current_products:
        sku = product.get('sku')
        if sku:
            current_skus.add(sku)
            if sku not in known_skus:
                new_products.append(product)
    
    # Отправляем уведомления о новых товарах
    if new_products:
        logger.info(f"🆕 Найдено новых товаров: {len(new_products)}")
        
        for product in new_products:
            notify_new_product(chat_id, product)
            known_skus.add(product.get('sku'))
        
        # Сохраняем обновленный список
        save_known_products(known_skus)
        
    else:
        logger.info("✅ Новых товаров нет")
    
    logger.info("="*60 + "\n")


def main():
    """Основной цикл работы бота"""
    
    logger.info("🚀 Запуск Lamoda Monitor Bot")
    logger.info(f"🎯 Категория: Adidas Originals")
    logger.info(f"⏰ Интервал проверки: {CHECK_INTERVAL // 60} минут")
    logger.info("="*60 + "\n")
    
    # Получаем chat_id
    chat_id = get_chat_id()
    
    if not chat_id:
        logger.error("❌ Chat ID не найден!")
        logger.info("💡 Отправьте любое сообщение боту для получения chat_id")
        logger.info(f"   Токен бота: {TELEGRAM_BOT_TOKEN}")
        
        # Ждем получения chat_id
        while not chat_id:
            time.sleep(10)
            chat_id = get_chat_id()
    
    logger.info(f"✅ Chat ID: {chat_id}")
    
    # Отправляем приветственное сообщение
    send_telegram_message(
        chat_id,
        "🤖 <b>Lamoda Monitor Bot запущен!</b>\n\n"
        "📍 Категория: Adidas Originals\n"
        f"⏰ Проверка каждый час\n"
        "🔔 Буду присылать уведомления о новых товарах"
    )
    
    # Первоначальная загрузка известных товаров
    known_skus = load_known_products()
    
    # Если база пустая - инициализируем текущими товарами
    if not known_skus:
        logger.info("📥 Инициализация базы известных товаров...")
        current_products = parse_lamoda_products(LAMODA_URL)
        
        for product in current_products:
            sku = product.get('sku')
            if sku:
                known_skus.add(sku)
        
        save_known_products(known_skus)
        logger.info(f"✅ Добавлено {len(known_skus)} товаров в базу")
    
    # Основной цикл мониторинга
    try:
        while True:
            try:
                check_for_new_products(chat_id)
            except Exception as e:
                logger.error(f"❌ Ошибка при проверке: {e}")
            
            # Ждем до следующей проверки
            logger.info(f"💤 Следующая проверка через {CHECK_INTERVAL // 60} минут\n")
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Остановка бота...")
        send_telegram_message(chat_id, "🛑 Lamoda Monitor Bot остановлен")


if __name__ == "__main__":
    main()

