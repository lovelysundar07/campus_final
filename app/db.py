import pymysql
import pymysql.cursors
from flask import g, current_app


def get_db():
    """Return the per-request DB connection stored in Flask g."""
    if 'db' not in g:
        g.db = pymysql.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,      # ← auto-commit every statement (no manual commit needed)
            connect_timeout=10,
            read_timeout=30,
            write_timeout=30,
        )
    return g.db
