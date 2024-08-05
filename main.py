import mysql
from mysql.connector import Error

def create_server_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

# Example usage
host = 'host'
user = 'root'
password = 'password'
database = 'dataname'
connection = create_server_connection(host, user, password, database)

def read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")


select_query = "SELECT * FROM customers"
results = read_query(connection, select_query)
for result in results:
    print(result)