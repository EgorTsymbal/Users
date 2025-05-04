from db_config import get_db_connection

def test_connection():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    print("Вы подключены к базе данных:", db_version)
    cursor.close()
    conn.close()

if __name__ == "__main__":
    test_connection()
