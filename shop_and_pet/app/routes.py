from flask import request, jsonify, send_from_directory
from db_config import get_db_connection
from app import app

# Главная страница
@app.route('/')
def index():
    return send_from_directory('static', 'pet_advice.html')

# Получение рекомендаций по породе
@app.route('/get_advice_by_breed', methods=['GET'])
def get_advice_by_breed():
    try:
        breed = request.args.get('breed')

        if not breed:
            return jsonify({"error": "Параметр breed обязателен"}), 400

        conn = get_db_connection()
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

        conn = get_db_connection()
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
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Сохранение профиля питомца
@app.route('/save_pet_profile', methods=['POST'])
def save_pet_profile():
    try:
        data = request.get_json()
        required_fields = ['name_pet', 'name_type', 'breed', 'age_y', 'age_m', 'allergies']

        if not all(field in data for field in required_fields):
            return jsonify({"error": "Не все обязательные поля заполнены"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO pet_profiles
                (name_pet, name_type, breed, age_y, age_m, allergies)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
            """,
            (data['name_pet'], data['name_type'], data['breed'],
             data['age_y'], data['age_m'], data['allergies'])
        )

        pet_id = cursor.fetchone()[0]
        conn.commit()

        return jsonify({
            "message": "Профиль питомца успешно сохранен",
            "pet_id": pet_id
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Добавление напоминания
@app.route('/add_reminder', methods=['POST'])
def add_reminder():
    try:
        data = request.get_json()
        required_fields = ['pet_id', 'procedure_type', 'procedure_name', 'next_date']

        if not all(field in data for field in required_fields):
            return jsonify({"error": "Не все обязательные поля заполнены"}), 400

        conn = get_db_connection()
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
        return jsonify({"message": "Напоминание успешно добавлено"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Получение напоминаний
@app.route('/get_reminders/<int:pet_id>', methods=['GET'])
def get_reminders(pet_id):
    try:
        conn = get_db_connection()
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
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Получение списка лекарств
@app.route('/get_medicines', methods=['GET'])
def get_medicines():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id_item, type_id, breed, weight, age_plus, structure, allergies, price FROM pet_medicine"
        )

        medicines = [{
            "id_item": row[0],
            "type_id": row[1],
            "breed": row[2],
            "weight": row[3],
            "age_plus": row[4],
            "structure": row[5],
            "allergies": row[6],
            "price": row[7]
        } for row in cursor.fetchall()]

        return jsonify({"medicines": medicines})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Получение информации о лекарстве по ID
@app.route('/get_medicine/<int:id_item>', methods=['GET'])
def get_medicine(id_item):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id_item, type_id, breed, weight, age_plus, structure, allergies, price FROM pet_medicine WHERE id_item = %s",
            (id_item,)
        )

        result = cursor.fetchone()

        if result:
            return jsonify({
                "id_item": result[0],
                "type_id": result[1],
                "breed": result[2],
                "weight": result[3],
                "age_plus": result[4],
                "structure": result[5],
                "allergies": result[6],
                "price": result[7]
            })
        else:
            return jsonify({"error": f"Лекарство с ID {id_item} не найдено"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Добавление нового лекарства
@app.route('/add_medicine', methods=['POST'])
def add_medicine():
    try:
        data = request.get_json()
        required_fields = ['type_id', 'breed', 'weight', 'age_plus', 'structure', 'price']

        if not all(field in data for field in required_fields):
            return jsonify({"error": "Не все обязательные поля заполнены"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO pet_medicine
                (type_id, breed, weight, age_plus, structure, allergies, price)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id_item
            """,
            (data['type_id'], data['breed'], data['weight'],
             data['age_plus'], data['structure'], data.get('allergies'), data['price'])
        )

        medicine_id = cursor.fetchone()[0]
        conn.commit()

        return jsonify({
            "message": "Лекарство успешно добавлено",
            "medicine_id": medicine_id
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
