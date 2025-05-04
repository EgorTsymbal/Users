from flask import Flask

# Создание экземпляра Flask
app = Flask(__name__)

# Импорт маршрутов
from app import routes
