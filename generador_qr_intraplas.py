from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import pyqrcode
import png
import os

app = Flask(__name__)
# Configuración de la base de datos PostgreSQL con SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost/empleados'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def generar_codigos_qr(QR_INTRAPLAS):
    """
    Genera códigos QR únicos para cada empleado desde la base de datos PostgreSQL
    Para QR_INTRAPLAS: Directorio donde se guardarán los códigos QR
    """
    try:
        # Asegurar que la carpeta de salida exista
        if not os.path.exists(QR_INTRAPLAS):
            os.makedirs(QR_INTRAPLAS)
        
        # Consulta usando SQLAlchemy
        with app.app_context():
            consulta = text("""
                SELECT id, nombre, departamento, tokens_almuerzo 
                FROM empleados_info
            """)
            
            print("Ejecutando consulta:", consulta)
            
            # Ejecutar la consulta usando SQLAlchemy
            resultado = db.session.execute(consulta)
            empleados = resultado.fetchall()
            
            # Contador para seguimiento
            total_generados = 0
            
            # Generar código QR para cada empleado
            for empleado in empleados:
                # Acceder a los valores usando nombre de columna
                id = empleado.id
                nombre = empleado.nombre
                departamento = empleado.departamento
                tokens_almuerzo = empleado.tokens_almuerzo
                
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
            
    except Exception as e:
        print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    # Definir la carpeta de salida
    QR_INTRAPLAS = 'C:/Users/andres.salcedo.INTRAPLAS/Desktop/tokens_intraplas2/QR_INTRAPLAS'
    
    # Llamar a la función para generar códigos QR
    generar_codigos_qr(QR_INTRAPLAS)