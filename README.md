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