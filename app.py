from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.permanent_session_lifetime = timedelta(minutes=10)

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
        return None

    return connection

def get_table_list(connection):
    query = "SHOW TABLES"
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        tables = cursor.fetchall()
        return [table[0] for table in tables]
    except Error as err:
        print(f"Error: '{err}'")
        return []

# Helper function to ensure a datetime object is naive
def make_naive(dt):
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session.permanent = True
        host = request.form['host']
        user = request.form['user']
        password = request.form['password']
        database = request.form['database']

        connection = create_server_connection(host, user, password, database)
        if connection:
            session['host'] = host
            session['user'] = user
            session['password'] = password
            session['database'] = database
            session['last_active'] = make_naive(datetime.now())  # Ensure it's naive

            tables = get_table_list(connection)
            return render_template('tables.html', tables=tables, connection_info=(host, user, password, database))
        else:
            return "Failed to connect to the database. Please check your credentials and try again."

    return render_template('index.html')

@app.route('/table/<table_name>', methods=['GET'])
def show_table(table_name):
    if 'host' in session:
        host = session['host']
        user = session['user']
        password = session['password']
        database = session['database']

        # Check if the session has timed out
        last_active = make_naive(session.get('last_active'))
        if last_active and (make_naive(datetime.now()) - last_active) > timedelta(minutes=10):
            session.pop('host', None)
            session.pop('user', None)
            session.pop('password', None)
            session.pop('database', None)
            session.pop('last_active', None)
            return "Session timed out. Please reconnect."

        session['last_active'] = make_naive(datetime.now())

        connection = create_server_connection(host, user, password, database)
        if connection:
            query = f"SELECT * FROM {table_name}"
            results = read_query(connection, query)
            # Render the tables.html template with the data
            tables = get_table_list(connection)
            return render_template('tables.html', tables=tables, connection_info=(host, user, password, database), results=results, table_name=table_name)
        else:
            return "Failed to retrieve the table data. Please check your connection."
    else:
        return redirect(url_for('tables'))

@app.route('/disconnect', methods=['GET'])
def disconnect():
    session.pop('host', None)
    session.pop('user', None)
    session.pop('password', None)
    session.pop('database', None)
    session.pop('last_active', None)
    return redirect(url_for('index', disconnected=True))


def read_query(connection, query):
    cursor = connection.cursor(dictionary=True)
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")
        return []

if __name__ == '__main__':
    app.run(debug=True)



# "user": "root",
# "password": "H0diemihicrastibi!",
# "host": "127.0.0.1",
# "database": "sql_invoicing"
