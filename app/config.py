# MySQL Database Configuration
MYSQL_HOST = os.environ.get(
    'MYSQL_HOST',
    os.environ.get('MYSQLHOST', '127.0.0.1')
)

MYSQL_PORT = int(os.environ.get(
    'MYSQL_PORT',
    os.environ.get('MYSQLPORT', 3306)
))

MYSQL_USER = os.environ.get(
    'MYSQL_USER',
    os.environ.get('MYSQLUSER', 'root')
)

MYSQL_PASSWORD = os.environ.get(
    'MYSQL_PASSWORD',
    os.environ.get('MYSQLPASSWORD', '')
)

MYSQL_DB = os.environ.get(
    'MYSQL_DB',
    'campus_events'
)

MYSQL_CURSORCLASS = 'DictCursor'