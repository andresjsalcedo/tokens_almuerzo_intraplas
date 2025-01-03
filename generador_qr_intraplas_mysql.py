import pyqrcode
import png
import os
import mysql.connector
from mysql.connector import Error

def generar_codigos_qr(QR_INTRAPLAS):

    #Genera códigos QR únicos para cada empleado desde la base de datos MySQL
    #Para QR_INTRAPLAS: Directorio donde se guardarán los códigos QR

    try:
        # Configuración de conexión a la base de datos MySQL
        conexion = mysql.connector.connect(
            host='localhost',  # nombre del host
            database='empleados',  # Nombre de  base de datos
            user='root',  # Tu nombre de usuario de MySQL
            password='root'  # Tu contraseña de MySQL
        )
        
        # Asegurar que la carpeta de salida exista
        if not os.path.exists(QR_INTRAPLAS):
            os.makedirs(QR_INTRAPLAS)
        
        # Crear un objeto cursor
        cursor = conexion.cursor()
        
        # Consulta para obtener información de empleados
        consulta = """ SELECT id, nombre, departamento, tokens_almuerzo FROM empleados_info """

        print(consulta)
        
        # Ejecutar la consulta
        cursor.execute(consulta)
        
        # Obtener todos los empleados
        empleados = cursor.fetchall()
        
        # Contador para seguimiento
        total_generados = 0
        
        # Generar código QR para cada empleado
        for empleado in empleados:
            # Desempaquetar detalles del empleado
            id = empleado[0]
            nombre = empleado[1]
            departamento = empleado[2]
            tokens_almuerzo = empleado[3]
            
            # Crear identificador único 
            id_unico = f"{id}"
            
            # Crear código QR
            qr = pyqrcode.create(id_unico, error='L')
            
            # Generar nombre de archivo 
            # Eliminar caracteres especiales del nombre para evitar errores
            nombre_limpio = ''.join(c for c in nombre if c.isalnum())
            departamento_limpio = ''.join(c for c in departamento if c.isalnum())
            
            nombre_archivo = f"{nombre_limpio}-{departamento_limpio}.png"
            ruta_archivo = os.path.join(QR_INTRAPLAS, nombre_archivo)
            
            # Guardar código QR
            qr.png(ruta_archivo, scale=6)
            
            total_generados += 1
            print(f"Generado código QR para {nombre} del {departamento}, cuenta con {tokens_almuerzo}")
        
        # Imprimir resumen
        print(f"\n--- Resumen ---")
        print(f"Total de códigos QR generados: {total_generados}")
        
        # Cerrar cursor y conexión
        cursor.close()
        conexion.close()
        
    except Error as error:
        print(f"Error al conectar o generar códigos QR: {error}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

# Definir la carpeta de salida
QR_INTRAPLAS = 'C:/Users/andres.salcedo.INTRAPLAS/Desktop/tokens_intraplas/QR_INTRAPLAS'

# Llamar a la función para generar códigos QR
generar_codigos_qr(QR_INTRAPLAS)