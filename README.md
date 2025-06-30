RehabilitationProject_FA
API на базе FastAPI и фронтенд на React для управления программами реабилитации пациентов, включая предсказание уровня физической активности и создание карт пациентов.
Структура проекта

backend/: FastAPI-приложение с эндпоинтами для работы с данными пациентов, предсказаниями и программами реабилитации.
frontend/: React-фронтенд для взаимодействия с API.
docker-compose.yaml: Конфигурация Docker для запуска бэкенда, фронтенда и базы данных PostgreSQL.
requirements.txt: Зависимости Python (предоставляется пользователем).

Инструкции по установке

Клонируйте репозиторий:
git clone <repository-url>
cd RehabilitationProject_FA


Установите зависимости:

Бэкенд: Предоставьте requirements.txt и выполните:pip install -r backend/requirements.txt


Фронтенд: Установите зависимости Node.js:cd frontend
npm install




Настройте переменные окружения:

Создайте файл .env в директории backend/ с содержимым:DATABASE_URL=postgresql://"Данные для подключения к базе данных"
GOOGLE_API_KEY=<your-google-api-key>




Запустите с помощью Docker:
docker-compose up --build


Доступ к приложению:

API бэкенда: http://localhost:8000
Фронтенд: http://localhost:3000
Документация API: http://localhost:8000/docs



Использование

Эндпоинты бэкенда:

GET /patients: Список всех пациентов.
GET /patients/{code}: Данные пациента по коду.
POST /predict-activity-manual: Предсказание уровня физической активности по введенным данным.
GET /rehab-program/{patient_code}: Программа реабилитации для пациента.
POST /create-card: Создание карты пациента.


Фронтенд:

Просмотр списка пациентов, их данных и программ реабилитации.
Отправка данных для предсказания активности и создание карт пациентов.



Примечания

Убедитесь, что база данных PostgreSQL rehab_db инициализирована с таблицей fa_numeric.
Файл модели CatBoost (catboost_physical_activity_model_2.cbm) должен быть размещен в /home/user/RehabilitationProject_FA/ внутри контейнера бэкенда.
Замените <your-google-api-key> на действительный ключ Google API для интеграции с Gemini.
