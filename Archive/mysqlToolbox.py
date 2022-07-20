import mysql.connector
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
    
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")

def clear_table(connection,tableName):
    query = 'DELETE FROM ' + tableName + ';'
    execute_query(connection=connection, query = query)

def addIndividual(connection, tableName, params):
    query = "INSERT INTO " + tableName + " VALUES(" + str(params) + ", FALSE,0,0);"
    print(query)
    execute_query(connection=connection, query = query)

def updateIndividual(connection, tableName, colName, val, identifierCol, identifierVal):
    query = "UPDATE " + tableName + " set " + colName + " = " + str(val) + " where " + identifierCol + " = " + str(identifierVal)
    print(query)
    execute_query(connection=connection, query= query)

    