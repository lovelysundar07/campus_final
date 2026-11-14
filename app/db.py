import pymysql
import pymysql.cursors
from flask import g, current_app


def get_db():
    """Return the per-request DB connection stored in Flask g."""

    if 'db' not in g:
        g.db = pymysql.connect(
            host=current_app.config['MYSQL_HOST'],
            port=current_app.config.get('MYSQL_PORT', 3306),
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
            connect_timeout=10,
            read_timeout=30,
            write_timeout=30,
        )

    return g.db