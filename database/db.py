import mysql.connector

def obtener_conexion():
    conexion = mysql.connector.connect(
        host="",
        user="tests",
        password="tests",
        database="test"
    )
    if conexion.is_connected():
        print("Conexión exitosa")
    return conexion