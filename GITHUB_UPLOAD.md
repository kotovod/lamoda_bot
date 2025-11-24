# 🚀 ЗАГРУЗКА В GITHUB - Пошаговая инструкция

## 📋 Вариант 1: Через SSH (рекомендуется)

### Шаг 1: Проверьте SSH ключ

```bash
# Проверьте есть ли SSH ключ
ls -la ~/.ssh/id_rsa.pub

# Если ключа нет - создайте:
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
# Нажимайте Enter на все вопросы
```

### Шаг 2: Добавьте SSH ключ в GitHub

```bash
# Скопируйте ключ
cat ~/.ssh/id_rsa.pub

# Или
pbcopy < ~/.ssh/id_rsa.pub  # Скопирует в буфер обмена
```

Затем:
1. Откройте https://github.com/settings/keys
2. Нажмите **"New SSH key"**
3. Вставьте ключ
4. Нажмите **"Add SSH key"**

### Шаг 3: Загрузите код

```bash
cd /Users/kotovod/Desktop/Lamoda_bot

# Добавьте remote (если еще не добавлен)
git remote add origin git@github.com:kotovod/lamoda_bot.git

# Запушьте код
git push -u origin main
```

---

## 📋 Вариант 2: Через HTTPS (проще, но менее безопасно)

### Шаг 1: Создайте Personal Access Token

1. Откройте https://github.com/settings/tokens
2. Нажмите **"Generate new token"** → **"Generate new token (classic)"**
3. Название: `Lamoda Bot`
4. Срок: `No expiration`
5. Права: отметьте **`repo`** (все подпункты)
6. Нажмите **"Generate token"**
7. **СКОПИРУЙТЕ ТОКЕН** (он больше не отобразится!)

### Шаг 2: Загрузите код

```bash
cd /Users/kotovod/Desktop/Lamoda_bot

# Добавьте remote через HTTPS
git remote add origin https://github.com/kotovod/lamoda_bot.git

# Запушьте (попросит username и пароль)
git push -u origin main

# Username: ваш GitHub username
# Password: ВСТАВЬТЕ ТОКЕН (не пароль от GitHub!)
```

---

## 📋 Вариант 3: Через GitHub Desktop (самый простой)

1. Скачайте: https://desktop.github.com/
2. Установите и войдите в GitHub аккаунт
3. File → Add Local Repository
4. Выберите `/Users/kotovod/Desktop/Lamoda_bot`
5. Нажмите **"Publish repository"**
6. Repository name: `lamoda_bot`
7. Нажмите **"Publish Repository"**

✅ Готово!

---

## ✅ Проверка что код загружен

Откройте в браузере:
```
https://github.com/kotovod/lamoda_bot
```

Должны увидеть все файлы проекта!

---

## 🎯 ПОСЛЕ ЗАГРУЗКИ - Деплой на сервер

### На сервере выполните:

```bash
# Подключитесь
ssh ваш_user@IP_сервера

# Установите git и Python
sudo apt update
sudo apt install -y git python3 python3-pip python3-venv

# Клонируйте репозиторий
cd ~
git clone https://github.com/kotovod/lamoda_bot.git
cd lamoda_bot

# Установите зависимости
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Настройте systemd
# ⚠️ ВАЖНО: Замените YOUR_USERNAME на результат команды whoami
whoami
nano lamoda-monitor.service
# Замените все YOUR_USERNAME на ваш username
# Сохраните: Ctrl+O, Enter, Ctrl+X

# Установите service
sudo cp lamoda-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable lamoda-monitor
sudo systemctl start lamoda-monitor

# Проверьте
sudo systemctl status lamoda-monitor
tail -f ~/lamoda_bot/lamoda_monitor.log
```

---

## 🔄 Обновление кода на сервере (в будущем)

```bash
ssh ваш_user@IP_сервера
cd ~/lamoda_bot
git pull
sudo systemctl restart lamoda-monitor
```

---

## 💡 Какой вариант выбрать?

- **SSH** - безопаснее, удобнее для частых обновлений
- **HTTPS + Token** - быстрее настроить, подходит для разовой загрузки
- **GitHub Desktop** - самый простой, подходит если не любите терминал

**Рекомендую: Вариант 2 (HTTPS + Token)** - быстро и просто! 🚀

