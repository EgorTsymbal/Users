from flask import Flask, request, jsonify, send_from_directory
from db_config import get_db_connection
import logging

app = Flask(__name__)


# Настройка логирования
logging.basicConfig(level=logging.DEBUG)

# Создаем экземпляр Flask
app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('static', 'pet_profile_form.html')

@app.route('/get_pet_names', methods=['GET'])
def get_pet_names():
    try:
        user_email = request.args.get('user_email')  # Получаем user_email из параметров запроса
        if not user_email:
            return jsonify({"error": "user_email is required"}), 400

        conn = get_db_connection('pet_care')
        cursor = conn.cursor()

        cursor.execute("SELECT pet_id, name_pet FROM pet_profiles WHERE user_email = %s", (user_email,))
        pet_names = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(pet_names)
    except Exception as e:
        logging.error(f"Ошибка при получении списка имен питомцев: {e}")
        return jsonify([]), 500


@app.route('/save_pet_profile', methods=['POST'])
def save_pet_profile():
    try:
        data = request.get_json()
        name_pet = data.get('name_pet')
        breed = data.get('breed')
        age_m = data.get('age_m')
        age_y = data.get('age_y')
        allergies = data.get('allergies')
        name_type = data.get('name_type')
        user_email = data.get('user_email')  # Получаем user_email из запроса

        if not all([name_type, breed, age_y, age_m, allergies, name_pet, user_email]):
            return jsonify({"error": "Все поля обязательны для заполнения"}), 400

        conn = get_db_connection('pet_care')
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO pet_profiles (name_type, breed, age_y, age_m, allergies, name_pet, user_email) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (name_type, breed, age_y, age_m, allergies, name_pet, user_email)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Профиль питомца успешно сохранен!"})

    except Exception as e:
        logging.error(f"Ошибка при сохранении профиля питомца: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/add_reminder', methods=['POST'])
def add_reminder():
    try:
        data = request.get_json()
        conn = get_db_connection('pet_care')
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO pet_reminders
                (pet_id, procedure_type, procedure_name, next_date, cycle_days, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (data['pet_id'], data['procedure_type'], data['procedure_name'],
             data['next_date'], data.get('cycle_days'), data.get('notes'))
        )

        conn.commit()
        return jsonify({"message": "Напоминание добавлено!"})

    except Exception as e:
        logging.error(f"Ошибка при добавлении напоминания: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/get_reminders/<int:pet_id>', methods=['GET'])
def get_reminders(pet_id):
    try:
        conn = get_db_connection('pet_care')
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, procedure_type, procedure_name, next_date, notes
            FROM pet_reminders
            WHERE pet_id = %s
              AND next_date BETWEEN CURRENT_DATE AND (CURRENT_DATE + INTERVAL '7 days')
              AND is_active = TRUE
            ORDER BY next_date
            """,
            (pet_id,)
        )

        reminders = [{
            "id": row[0],
            "procedure_type": row[1],
            "procedure_name": row[2],
            "next_date": str(row[3]),
            "notes": row[4]
        } for row in cursor.fetchall()]

        return jsonify({"reminders": reminders})

    except Exception as e:
        logging.error(f"Ошибка при получении напоминаний: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/add_procedure', methods=['POST'])
def add_procedure():
    try:
        data = request.get_json()
        conn = get_db_connection('pet_care')
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO pet_procedures (pet_id, procedure_type, procedure_name, procedure_date, name_type, breed)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (data['pet_id'], data['procedure_type'], data['procedure_name'], data['procedure_date'], data['name_type'], data['breed'])
        )

        conn.commit()
        return jsonify({"message": "Процедура добавлена!"})

    except Exception as e:
        logging.error(f"Ошибка при добавлении процедуры: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/get_advice/<int:pet_id>', methods=['GET'])
def get_advice(pet_id):
    try:
        conn = get_db_connection('pet_care')
        cursor = conn.cursor()

        # Пример ответа, замените на реальную логику
        cursor.execute(
            "SELECT name FROM pet_profiles WHERE id = %s",
            (pet_id,)
        )
        pet_name = cursor.fetchone()[0]
        advice = [
            "Проверьте питание питомца",
            "Регулярно посещайте ветеринара",
            "Убедитесь, что питомец получает достаточно воды"
        ]

        return jsonify({"pet_name": pet_name, "advice": advice})

    except Exception as e:
        logging.error(f"Ошибка при получении совета: {e}")
        return jsonify({"error": str(e)}), 500

# Получение рекомендаций по породе
@app.route('/get_advice_by_breed', methods=['GET'])
def get_advice_by_breed():
    try:
        breed = request.args.get('breed')

        if not breed:
            return jsonify({"error": "Параметр breed обязателен"}), 400

        conn = get_db_connection('pet_care')
        cursor = conn.cursor()

        # Запрос к таблице recomendation_for_pet по полю breed
        cursor.execute(
            "SELECT name_type, care_recommendation FROM recomendation_for_pet WHERE breed = %s",
            (breed,)
        )

        result = cursor.fetchone()

        if result:
            return jsonify({
                "breed": breed,
                "animal_type": result[0],
                "care_recommendation": result[1]
            })
        else:
            return jsonify({"error": f"Рекомендации для породы '{breed}' не найдены"}), 404

    except Exception as e:
        logging.error(f"Ошибка при получении рекомендаций по породе: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Получение списка пород для типа животного
@app.route('/get_breeds', methods=['GET'])
def get_breeds():
    try:
        animal_type = request.args.get('animal_type')

        if not animal_type:
            return jsonify({"error": "Параметр animal_type обязателен"}), 400

        conn = get_db_connection('pet_care')
        cursor = conn.cursor()

        cursor.execute(
            "SELECT breed FROM recomendation_for_pet WHERE name_type = %s ORDER BY breed",
            (animal_type,)
        )

        breeds = [row[0] for row in cursor.fetchall()]

        return jsonify({
            "animal_type": animal_type,
            "breeds": breeds
        })

    except Exception as e:
        logging.error(f"Ошибка при получении списка пород: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Новый маршрут для получения рекомендаций по аллергиям
@app.route('/get_recommendations_by_allergies', methods=['GET'])
def get_recommendations_by_allergies():
    return send_from_directory('static', 'get_recommendations_by_allergies.html')

@app.route('/recommend_food', methods=['GET'])
def recommend_food():
    try:
        pet_id = request.args.get('pet_id')
        pet_data = get_pet_data(pet_id)
        if not pet_data:
            return jsonify({'message': 'Питомец не найден'})

        allergies = pet_data['allergies']
        breed = pet_data['breed']

        # Если аллергий нет, возвращаем все товары, подходящие по породе
        if not allergies:
            allergies = ''

        recommended_food = get_recommended_items(allergies, breed, 'pet_food')
        if recommended_food:
            recommendations = [
                {
                    "name": item[1],
                    "description": item[5],
                    "price": item[7]
                }
                for item in recommended_food
            ]
            return jsonify({'recommendations': recommendations})
        else:
            return jsonify({'recommendations': []})
    except Exception as e:
        logging.error(f"Ошибка при рекомендации корма: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/recommend_medicine', methods=['GET'])
def recommend_medicine():
    try:
        pet_id = request.args.get('pet_id')
        pet_data = get_pet_data(pet_id)
        if not pet_data:
            return jsonify({'message': 'Питомец не найден'})

        allergies = pet_data['allergies']
        breed = pet_data['breed']

        # Если аллергий нет, возвращаем все товары, подходящие по породе
        if not allergies:
            allergies = ''

        recommended_medicine = get_recommended_items(allergies, breed, 'pet_medicine')
        if recommended_medicine:
            recommendations = [
                {
                    "name": item[1],
                    "description": item[5],
                    "price": item[7]
                }
                for item in recommended_medicine
            ]
            return jsonify({'recommendations': recommendations})
        else:
            return jsonify({'recommendations': []})
    except Exception as e:
        logging.error(f"Ошибка при рекомендации лекарства: {e}")
        return jsonify({"error": str(e)}), 500

def get_pet_data(pet_id):
    try:
        conn = get_db_connection('pet_care')
        cursor = conn.cursor()
        cursor.execute("SELECT allergies, breed FROM pet_profiles WHERE pet_id = %s", (pet_id,))
        pet_data = cursor.fetchone()
        conn.close()
        if pet_data:
            return {'allergies': pet_data[0], 'breed': pet_data[1]}
        return None
    except Exception as e:
        logging.error(f"Ошибка при получении данных питомца: {e}")
        return None

def get_recommended_items(allergies, breed, table_name):
    try:
        conn = get_db_connection('shop')
        cursor = conn.cursor()

        # Если аллергий нет, выбираем все товары, подходящие по породе
        if allergies == '':
            cursor.execute(
                f"SELECT * FROM {table_name} WHERE breed = %s",
                (breed,)
            )
        else:
            # Ищем товары, где аллергии НЕ совпадают с аллергиями питомца, а порода совпадает
            cursor.execute(
                f"""
                SELECT * FROM {table_name}
                WHERE allergies NOT LIKE %s AND breed = %s
                """,
                (f"%{allergies}%", breed)
            )

        items = cursor.fetchall()
        conn.close()
        return items
    except Exception as e:
        logging.error(f"Ошибка при получении рекомендованных товаров: {e}")
        return []

if __name__ == '__main__':
    app.run(debug=True)
