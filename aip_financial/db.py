import re
from datetime import datetime
import pandas as pd

# mysql.connector හෝ PyMySQL වෙතින් සුදුසු Driver එක ස්වයංක්‍රීයව තෝරාගැනීම
try:
    import mysql.connector
    from mysql.connector import Error
    USE_CONNECTOR = True
except ImportError:
    try:
        import pymysql
        pymysql.install_as_MySQLdb()
        Error = pymysql.MySQLError
        USE_CONNECTOR = False
    except ImportError:
        raise ModuleNotFoundError("කරුණාකර requirements.txt ගොනුවට 'mysql-connector-python' හෝ 'PyMySQL' ඇතුළත් කරන්න.")

# =========================================================================
# MYSQL DATABASE CONFIGURATION
# =========================================================================
DB_CONFIG = {
    "host": "aip.2026.amparapiriven.lk",
    "database": "amparapi_aip_2026",
    "user": "amparapi_aip_2026",
    "password": "Aippiriven@1234",
    "port": 3306,
    "charset": "utf8mb4"    
}
# db.py හි Database සැකසුම්
DB_CONFIG = {
    "host": "aip.2026.amparapiriven.lk",
    "database": "amparapi_aip_2026",
    "user": "amparapi_aip_2026",
    "password": "Aippiriven@1234",
    "port": 3306,
    "charset": "utf8mb4",
    "connect_timeout": 5  # තත්පර 5කට වඩා Freeze වීම වළක්වයි
}

def get_connection():
    """MySQL සම්බන්ධතාවය ලබා ගැනීම."""
    try:
        if USE_CONNECTOR:
            conn = mysql.connector.connect(**DB_CONFIG, autocommit=True, use_unicode=True)
        else:
            conn = pymysql.connect(**DB_CONFIG, autocommit=True, cursorclass=pymysql.cursors.DictCursor)
        return conn
    except Error:
        # Remote සම්බන්ධ වීමට නොහැකි වුවහොත් localhost උත්සාහ කිරීම
        fallback = DB_CONFIG.copy()
        fallback["host"] = "localhost"
        if USE_CONNECTOR:
            return mysql.connector.connect(**fallback, autocommit=True, use_unicode=True)
        else:
            return pymysql.connect(**fallback, autocommit=True, cursorclass=pymysql.cursors.DictCursor)
