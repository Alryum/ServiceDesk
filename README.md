# ServiceDesk - Система обработки пользовательских обращений

---

## 🛠️ **Стек технологий**

### **Основной стек:**
- **Backend:** Django + Django REST Framework  
- **База данных:** PostgreSQL  
- **API документация:** Swagger(drf-yasg)  
- **Тесты:** pytest  
- **Фоновые таски:** Сelery  
- **Брокер сообщений для Celery:** Redis  
- **Контейнеризация:** Docker + docker compose  

---

## 📦 **Установка и запуск проекта**

### 1. **Клонируйте репозиторий**
```bash
git clone https://github.com/Alryum/ServiceDesk.git
cd ServiceDesk   
```

### 2. **Настройте виртуальное окружение и установите зависимости**  
```bash
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate (Windows)
pip install -r requirements.txt 
```  
- Переименуйте файл ".env.example" в ".env"  

### 3. **Запуск проекта**  
- **Контейнеры**  
```bash
docker compose up -d --build
```
- **Миграции**
```bash
docker compose exec web python manage.py migrate
```  
- **Запуск тестов** 
```bash
docker compose exec web pytest
```  

## 📊 **Доступ и документация**

### 🚀 **Документация API**

Документация по доступному API представлена через **Swagger**:  
[http://localhost:8000/swagger/](http://localhost:8000/swagger/)

---

### 🛠️ **Админ-панель**

Админ-панель Django для управления тикетами и пользователями:  
[http://localhost:8000/admin/](http://localhost:8000/admin/)

---

### 👤 **Создание суперпользователя для админки**

Если вы используете Docker, используйте следующую команду для создания суперпользователя:  

```bash
docker compose exec web python manage.py createsuperuser
```