db = {
    'user' : 'root',
    'password' : '3575',
    'host' : 'localhost',
    'port' : 3306,
    'database' : 'aii_db'
}

DB_URL = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"