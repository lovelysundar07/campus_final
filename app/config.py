import os
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env')

if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()   

class Config:

    # MySQL Database Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or os.environ.get('MYSQLHOST', '127.0.0.1')

    MYSQL_PORT = int(
        os.environ.get('MYSQL_PORT') or
        os.environ.get('MYSQLPORT', 3306)
    )

    MYSQL_USER = os.environ.get('MYSQL_USER') or os.environ.get('MYSQLUSER', 'root')

    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or os.environ.get('MYSQLPASSWORD', '')

    MYSQL_DB = (
        os.environ.get('MYSQL_DB') or
        os.environ.get('MYSQLDATABASE') or
        'campus_events'
    )

    MYSQL_CURSORCLASS = 'DictCursor'

    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Keep your other existing configuration here