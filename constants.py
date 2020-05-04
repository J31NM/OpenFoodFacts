import os

MYSQL_USER = os.environ.get('OC5_MYSQL_USER', 'root')
MYSQL_PWD = os.environ.get('OC5_MYSQL_PWD', '')
MYSQL_HOST = os.environ.get('OC5_MYSQL_HOST', '127.0.0.1')
MYSQL_DATABASE = 'openfoodfacts_db'
# pylint: disable=W0614
