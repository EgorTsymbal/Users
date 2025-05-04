from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Создание экземпляра приложения Flask
app = Flask(__name__)

# Конфигурация базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:lonely@localhost:5432/forum'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация расширений
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Модель пользователя
class ForumUser(db.Model):
    __tablename__ = 'forum_user'

    id = db.Column(db.Integer, primary_key=True)
    log = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    token = db.Column(db.String(255))

    # Связь с питомцами
    pets = db.relationship('PetProfile', backref='user', lazy=True)

# Модель профиля питомца
class PetProfile(db.Model):
    __tablename__ = 'pet_profiles'

    pet_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('forum_user.id'), nullable=False)
    name_type = db.Column(db.String(255))
    breed = db.Column(db.String(255))
    age_y = db.Column(db.Integer)
    age_m = db.Column(db.Integer)
    allergies = db.Column(db.Text)
    name_pet = db.Column(db.String(255))

    def to_dict(self):
        return {
            "pet_id": self.pet_id,
            "user_id": self.user_id,
            "name_type": self.name_type,
            "breed": self.breed,
            "age_y": self.age_y,
            "age_m": self.age_m,
            "allergies": self.allergies,
            "name_pet": self.name_pet
        }

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)
