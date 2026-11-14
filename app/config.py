import os
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env')

if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()   

class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-secret')

    # MySQL Configuration
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

    # File Upload Configuration
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(__file__), 'static', 'uploads'
    )

    PPT_FOLDER = os.path.join(UPLOAD_FOLDER, 'ppts')
    CERT_FOLDER = os.path.join(UPLOAD_FOLDER, 'certificates')
    REPORT_FOLDER = os.path.join(UPLOAD_FOLDER, 'reports')
    BANNER_FOLDER = os.path.join(UPLOAD_FOLDER, 'banners')

    MAX_CONTENT_LENGTH = 50 * 1024 * 1024

    ALLOWED_PPT_EXTENSIONS = {'ppt', 'pptx', 'pdf'}
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # Gemini AI
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

    # College Information
    COLLEGE_NAME = 'MS College'
    COLLEGE_TAGLINE = 'Empowering Minds, Building Futures'

    # Session
    PERMANENT_SESSION_LIFETIME = 86400


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}