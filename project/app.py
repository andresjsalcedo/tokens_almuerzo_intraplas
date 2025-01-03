from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import datetime

app = Flask(__name__, static_folder='static')

# PostgreSQL configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5432/empleados'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class EscanerQRWeb:
    # Change table name in queries
    def obtener_empleados(self):
        try:
            result = db.session.execute(text("""
            SELECT id, nombre, departamento, tokens_almuerzo 
            FROM empleados_info
        """)).fetchall()
            empleados = [dict(zip(['id', 'nombre', 'departamento', 'tokens_almuerzo'], row)) for row in result]
            return empleados
        except Exception as e:
            print(f"Error al obtener empleados: {e}")
        return []
    
    @app.route('/empleados')
    def index():
        escaner = EscanerQRWeb()
        empleados = escaner.obtener_empleados()
        if not empleados:
            print("No se encontraron empleados")  # Debug line
        return render_template('tokens_intraplas.html',  # Match your HTML filename
                         empleados=empleados)
            
    def actualizar_empleado(self, id, nombre, departamento, tokens):
        try:
            db.session.execute(text("""
                UPDATE empleados_info 
                SET nombre = :nombre, departamento = :departamento, tokens_almuerzo = :tokens 
                WHERE id = :id
            """), {'nombre': nombre, 'departamento': departamento, 'tokens': tokens, 'id': id})
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar empleado: {e}")
        db.session.rollback()
        return False

    def obtener_total_empleados(self):
        try:
            result = db.session.execute(text('SELECT COUNT(*) FROM empleados_info'))
            return result.scalar()
        except Exception as e:
            print(f"Error al obtener total de empleados: {e}")
            return 0


@app.route('/registrar', methods=['POST'])
def registrar():
    try:
        db.session.execute("""
            INSERT INTO usuarios (username, password, email, fullname) 
            VALUES (:username, :password, :email, :fullname)
        """, {
            'username': request.form.get('username'),
            'password': request.form.get('password'),
            'email': request.form.get('email'),
            'fullname': request.form.get('fullname')
        })
        db.session.commit()
        return render_template('login.html', redirect_url='/')
    except Exception as e:
        db.session.rollback()
        print(f"Error al registrar usuario: {e}")
        return render_template('login.html', error="Error al registrar usuario")

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/Dashboard')
def dashboard():
    escaner = EscanerQRWeb()
    total_usuarios = escaner.obtener_total_empleados()
    return render_template('Dashboard.html', total_usuarios=total_usuarios)

@app.route('/api/total-usuarios')
def obtener_total_usuarios():
    escaner = EscanerQRWeb()
    total = escaner.obtener_total_empleados()
    return jsonify({'total': total})

@app.route('/actualizar_empleado', methods=['POST'])
def actualizar_empleado_route():
    escaner = EscanerQRWeb()
    if escaner.actualizar_empleado(
        request.form.get('id'),
        request.form.get('nombre'),
        request.form.get('departamento'),
        request.form.get('tokens')
    ):
        return jsonify({'success': True})
    return jsonify({'success': False})

if __name__ == '__main__':
    app.run(debug=True)