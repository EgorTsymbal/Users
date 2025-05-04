from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from db_config import get_db_connection
import logging
from datetime import timedelta
import psycopg2

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)

# Создаем экземпляр Flask
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.permanent_session_lifetime = timedelta(days=1)

# Инициализация SQLAlchemy
db = SQLAlchemy()

# Конфигурация БД
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:lonely@localhost:5432/shop'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализируем SQLAlchemy с приложением
db.init_app(app)


# Модель CartItem
class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    item_id = db.Column(db.Integer, nullable=False)
    item_type = db.Column(db.String(50), nullable=False)  # 'pet_food' или 'pet_medicine'
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "item_id": self.item_id,
            "item_type": self.item_type,
            "quantity": self.quantity,
            "price": self.price
        }


@app.before_request
def before_request():
    session.permanent = True


@app.route('/')
def index():
    return redirect(url_for('shop'))


@app.route('/shop')
def shop():
    if 'user_id' not in session:
        session['user_id'] = 1  # В реальном приложении используйте аутентификацию
    return render_template('shop.html')


@app.route('/cart')
def cart():
    if 'user_id' not in session:
        return redirect(url_for('shop'))

    user_id = session['user_id']
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    total_price = sum(item.quantity * item.price for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)


@app.route('/api/breeds', methods=['GET'])
def get_breeds_by_type():
    try:
        animal_type = request.args.get('animal_type')
        product_type = request.args.get('product_type', 'pet_food')

        if not animal_type:
            return jsonify({"error": "Не указан тип животного"}), 400

        conn = get_db_connection('shop')
        cursor = conn.cursor()

        # Определяем условия фильтрации по типу животного
        if animal_type == 'Кошка':
            breed_condition = "breed IN ('Персидская', 'Сфинкс', 'Мейн-кун', 'Британская', 'Сиамская')"
        elif animal_type == 'Собака':
            breed_condition = "breed IN ('Лабрадор', 'Немецкая овчарка', 'Чихуахуа', 'Хаски', 'Бульдог')"
        elif animal_type == 'Птица':
            breed_condition = "breed IN ('Волнистый попугай', 'Ара')"
        else:
            breed_condition = "1=1"  # Все породы

        query = f"""
            SELECT DISTINCT breed 
            FROM {product_type}
            WHERE {breed_condition}
            ORDER BY breed
        """

        cursor.execute(query)
        breeds = [row[0] for row in cursor.fetchall()]
        conn.close()

        return jsonify(breeds)

    except Exception as e:
        logging.error(f"Ошибка при получении пород: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        product_type = request.args.get('type')
        breed_filter = request.args.get('breed')
        age_filter = request.args.get('age')
        animal_type_filter = request.args.get('animal_type')

        if product_type not in ['pet_food', 'pet_medicine']:
            return jsonify({"error": "Неверный тип продукта"}), 400

        conn = get_db_connection('shop')
        cursor = conn.cursor()

        query = f"SELECT * FROM {product_type}"
        conditions = []
        params = []

        if breed_filter:
            conditions.append("breed = %s")
            params.append(breed_filter)
        if age_filter:
            conditions.append("age_plus = %s")
            params.append(age_filter)
        if animal_type_filter:
            if animal_type_filter == 'Кошка':
                conditions.append("breed IN ('Персидская', 'Сфинкс', 'Мейн-кун', 'Британская', 'Сиамская')")
            elif animal_type_filter == 'Собака':
                conditions.append("breed IN ('Лабрадор', 'Немецкая овчарка', 'Чихуахуа', 'Хаски', 'Бульдог')")
            elif animal_type_filter == 'Птица':
                conditions.append("breed IN ('Волнистый попугай', 'Ара')")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cursor.execute(query, params)
        products = cursor.fetchall()
        conn.close()

        product_list = [{
            "id": p[0], "name": p[1], "breed": p[2], "weight": p[3],
            "age_plus": p[4], "structure": p[5], "allergies": p[6],
            "price": p[7], "type": product_type
        } for p in products]

        return jsonify(product_list)

    except Exception as e:
        logging.error(f"Ошибка при получении продуктов: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    try:
        if 'user_id' not in session:
            return jsonify({"error": "Требуется авторизация"}), 401

        data = request.get_json()
        user_id = session['user_id']
        item_id = data.get('item_id')
        item_type = data.get('item_type')
        quantity = data.get('quantity', 1)
        price = data.get('price')

        if not all([item_id, item_type, price]):
            return jsonify({"error": "Все поля обязательны для заполнения"}), 400

        existing_item = CartItem.query.filter_by(
            user_id=user_id,
            item_id=item_id,
            item_type=item_type
        ).first()

        if existing_item:
            existing_item.quantity += quantity
        else:
            new_item = CartItem(
                user_id=user_id,
                item_id=item_id,
                item_type=item_type,
                quantity=quantity,
                price=price
            )
            db.session.add(new_item)

        db.session.commit()
        return jsonify({"message": "Товар добавлен в корзину"}), 201

    except Exception as e:
        logging.error(f"Ошибка при добавлении товара в корзину: {e}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/api/cart', methods=['GET'])
def get_cart():
    try:
        if 'user_id' not in session:
            return jsonify({"error": "Требуется авторизация"}), 401

        user_id = session['user_id']
        cart_items = CartItem.query.filter_by(user_id=user_id).all()
        return jsonify([item.to_dict() for item in cart_items])

    except Exception as e:
        logging.error(f"Ошибка при получении корзины: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/cart', methods=['DELETE'])
def clear_cart():
    try:
        if 'user_id' not in session:
            return jsonify({"error": "Требуется авторизация"}), 401

        user_id = session['user_id']
        CartItem.query.filter_by(user_id=user_id).delete()
        db.session.commit()

        return jsonify({"message": "Корзина очищена"})

    except Exception as e:
        logging.error(f"Ошибка при очистке корзины: {e}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/cart/<int:item_id>', methods=['PUT'])
def update_cart_item(item_id):
    try:
        if 'user_id' not in session:
            return jsonify({"error": "Требуется авторизация"}), 401

        data = request.get_json()
        quantity = data.get('quantity')

        if quantity is None:
            return jsonify({"error": "Количество обязательно"}), 400

        cart_item = CartItem.query.filter_by(
            id=item_id,
            user_id=session['user_id']
        ).first_or_404()

        cart_item.quantity = quantity
        db.session.commit()
        return jsonify({"message": "Товар обновлен"})

    except Exception as e:
        logging.error(f"Ошибка при обновлении товара: {e}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/api/cart/<int:item_id>', methods=['DELETE'])
def remove_from_cart(item_id):
    try:
        if 'user_id' not in session:
            return jsonify({"error": "Требуется авторизация"}), 401

        cart_item = CartItem.query.filter_by(
            id=item_id,
            user_id=session['user_id']
        ).first_or_404()

        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({"message": "Товар удален"})

    except Exception as e:
        logging.error(f"Ошибка при удалении товара: {e}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/api/checkout', methods=['POST'])
def checkout():
    try:
        if 'user_id' not in session:
            return jsonify({"error": "Требуется авторизация"}), 401

        user_id = session['user_id']
        cart_items = CartItem.query.filter_by(user_id=user_id).all()

        if not cart_items:
            return jsonify({"error": "Корзина пуста"}), 400

        # Здесь можно добавить логику оформления заказа
        for item in cart_items:
            db.session.delete(item)
        db.session.commit()

        return jsonify({
            "message": "Заказ оформлен",
            "order_id": "12345"  # В реальном приложении вернуть реальный ID заказа
        })

    except Exception as e:
        logging.error(f"Ошибка при оформлении заказа: {e}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)