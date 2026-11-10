import os
from dotenv import load_dotenv

# Load .env relative to config.py location
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'msv-campus-events-secret-2024-xK9#mPq')
    
    # MySQL Database
    MYSQL_HOST = os.environ.get('MYSQL_HOST', '127.0.0.1')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'campus_events')
    MYSQL_CURSORCLASS = 'DictCursor'
    
    # File Upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    PPT_FOLDER = os.path.join(UPLOAD_FOLDER, 'ppts')
    CERT_FOLDER = os.path.join(UPLOAD_FOLDER, 'certificates')
    REPORT_FOLDER = os.path.join(UPLOAD_FOLDER, 'reports')
    BANNER_FOLDER = os.path.join(UPLOAD_FOLDER, 'banners')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max upload
    ALLOWED_PPT_EXTENSIONS = {'ppt', 'pptx', 'pdf'}
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Google Gemini AI
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    
    # College Info
    COLLEGE_NAME = 'MS College'
    COLLEGE_TAGLINE = 'Empowering Minds, Building Futures'
    
    # Session
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
