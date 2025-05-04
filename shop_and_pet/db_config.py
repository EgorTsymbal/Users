import psycopg2
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def get_db_connection(db_name='shop'):
    db_configs = {
        'shop': {
            'dbname': 'shop',
            'user': 'postgres',
            'password': 'lonely',
            'host': 'localhost',
            'port': '5432'
        },
        'pet_care': {
            'dbname': 'pet_care',
            'user': 'postgres',
            'password': 'lonely',
            'host': 'localhost',
            'port': '5432'
        }
    }

    if db_name not in db_configs:
        raise ValueError(f"Unknown database name: {db_name}")

    try:
        conn = psycopg2.connect(**db_configs[db_name])
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL database {db_name}: {e}")
        raise


def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:lonely@localhost:5432/shop'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    db.init_app(app)

    with app.app_context():
        db.create_all()