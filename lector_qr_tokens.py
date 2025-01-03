import cv2
from pyzbar.pyzbar import decode
import numpy as np
from datetime import datetime
import openpyxl as xl
import time
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)
# Configuración de la base de datos PostgreSQL con SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost/empleados'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class EscanerQR:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.codigos_registrados = set()
        self.carpeta_destino = 'C:/Users/andres.salcedo.INTRAPLAS/Desktop/tokens_intraplas2/registro_tokens_intraplas'
        
        if not os.path.exists(self.carpeta_destino):
            os.makedirs(self.carpeta_destino)

    def validar_codigo_qr(self, codigo):
        try:
            # Usando SQLAlchemy con text() para consultas SQL directas
            consulta = text("""SELECT id, nombre, departamento, tokens_almuerzo 
                             FROM empleados_info 
                             WHERE id = :codigo AND tokens_almuerzo > 0""")
            
            resultado = db.session.execute(consulta, {'codigo': codigo})
            empleado_info = resultado.fetchone()
            
            if empleado_info:
                self.descontar_token(empleado_info.id)
                # Convertir el resultado a diccionario
                return {
                    'id': empleado_info.id,
                    'nombre': empleado_info.nombre,
                    'departamento': empleado_info.departamento,
                    'tokens_almuerzo': empleado_info.tokens_almuerzo
                }
            return None
            
        except Exception as e:
            print(f"Error al validar código: {e}")
            db.session.rollback()
            return None

    def descontar_token(self, empleado_id):
        try:
            update_query = text("""UPDATE empleados_info 
                                 SET tokens_almuerzo = tokens_almuerzo - 1 
                                 WHERE id = :empleado_id""")
            
            db.session.execute(update_query, {'empleado_id': empleado_id})
            db.session.commit()
            
        except Exception as e:
            print(f"Error al descontar token: {e}")
            db.session.rollback()

    def registrar_entrada(self, empleados_info, hora, fecha):
        try:
            wb = xl.Workbook()
            hoja = wb.active
            hoja.title = "Consumo_tokens"
            
            hoja['A1'] = 'ID'
            hoja['B1'] = 'NOMBRE'
            hoja['C1'] = 'ÁREA'
            hoja['D1'] = 'TOKENS RESTANTES'
            hoja['E1'] = 'FECHA'
            hoja['F1'] = 'HORA'
            
            tokens_actualizados = empleados_info['tokens_almuerzo'] - 1
            hoja['A2'] = empleados_info['id']
            hoja['B2'] = empleados_info['nombre']
            hoja['C2'] = empleados_info['departamento']
            hoja['D2'] = tokens_actualizados
            hoja['E2'] = fecha
            hoja['F2'] = hora
            
            nombre_archivo = f"{fecha}.xlsx"
            ruta_completa = os.path.join(self.carpeta_destino, nombre_archivo)
            
            wb.save(ruta_completa)
            print(f"Token de almuerzo de {empleados_info['nombre']} del área {empleados_info['departamento']} fue consumido el {fecha} a las {hora}, tokens restantes: {tokens_actualizados}") 
         
        except Exception as e:
            print(f"Error al registrar el consumo de token: {e}")

    def iniciar_escaneo(self):
        with app.app_context():  # Necesario para trabajar con SQLAlchemy fuera de una ruta Flask
            while True:
                ret, frame = self.cap.read()
                
                cv2.putText(frame, 'Presiona ESC para salir', (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
                
                cv2.rectangle(frame, (170, 100), (470, 400), (0, 255, 0), 2)
                
                hora = datetime.now().strftime('%H:%M:%S')
                fecha = datetime.now().strftime('%Y-%m-%d')
                
                for codigo_qr in decode(frame):
                    codigo = codigo_qr.data.decode('utf-8')
                    
                    if codigo not in self.codigos_registrados:
                        empleados_info = self.validar_codigo_qr(codigo)
                        
                        if empleados_info:
                            self.registrar_entrada(empleados_info, hora, fecha)
                            self.codigos_registrados.add(codigo)
                            
                            pts = np.array([codigo_qr.polygon], np.int32)
                            pts = pts.reshape((-1, 1, 2))
                            cv2.polylines(frame, [pts], True, (0, 255, 0), 5)
                            cv2.putText(frame, 'ENTRADA REGISTRADA', 
                                        (codigo_qr.rect.left, codigo_qr.rect.top - 30), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        else:
                            cv2.putText(frame, 'SIN TOKENS DISPONIBLES', 
                                        (codigo_qr.rect.left, codigo_qr.rect.top - 30), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                             
                    elif codigo in self.codigos_registrados:
                        pts = np.array([codigo_qr.polygon], np.int32)
                        pts = pts.reshape((-1, 1, 2))
                        cv2.polylines(frame, [pts], True, (0, 255, 0), 5)
                        cv2.putText(frame, 'REGISTRO YA EXISTENTE', 
                                    (codigo_qr.rect.left, codigo_qr.rect.top - 30), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                cv2.imshow('Escáner QR', frame)
                
                if cv2.waitKey(1) == 27:
                    break
            
            self.cap.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    escaner = EscanerQR()
    escaner.iniciar_escaneo()