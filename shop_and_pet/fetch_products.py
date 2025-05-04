import requests
from db_config import get_db_connection

def get_veterinary_products():
    # URL API Rubrikator
    api_url = "https://rubrikator.org/api/v1/items/domashnie-zhivotnie-i-rastenia/veterinarnye-sredstva"

    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка при запросе к API: {response.status_code}")
        return None

def save_products_to_db(products):
    conn = get_db_connection()
    cursor = conn.cursor()

    for product in products:
        cursor.execute(
            "INSERT INTO products (name, description) VALUES (%s, %s)",
            (product['name'], product['description'])
        )

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    products = get_veterinary_products()
    if products:
        save_products_to_db(products)
        print("Продукты успешно сохранены в базу данных.")
    else:
        print("Не удалось получить данные о продуктах.")
