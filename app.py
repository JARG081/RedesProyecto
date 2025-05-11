from flask import Flask, request, render_template, jsonify  
from datetime import datetime
import json
import os


app = Flask(__name__)

# Ruta del archivo con nombres
RUTA_NOMBRES = os.path.join(os.path.dirname(__file__), 'tarjetas.json')

# Estado por UID (para alternar entre ingreso/salida)
estado_por_codigo = {}

# Lista para guardar los registros
log = []

# Estado de autorización por UID
autorizado_por_codigo = {}

# Cargar nombres desde tarjetas.json
try:
    with open(RUTA_NOMBRES, 'r') as archivo:
        nombres_por_codigo = json.load(archivo)
except FileNotFoundError:
    nombres_por_codigo = {}

@app.route('/api/log')
def obtener_log():
    return jsonify(log)

@app.route('/')
def index():
    return render_template('index.html', log=log, autorizado_por_codigo=autorizado_por_codigo)

@app.route('/registro', methods=['POST'])
def recibir_datos():
    data = request.get_json()
    if not data or 'uid' not in data:
        return "Datos no válidos", 400

    codigo = data['uid']
    hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Alternar ingreso/salida
    ultimo_estado = estado_por_codigo.get(codigo, 'SALIDA')
    nuevo_estado = 'INGRESO' if ultimo_estado == 'SALIDA' else 'SALIDA'
    estado_por_codigo[codigo] = nuevo_estado

    # Obtener nombre desde el diccionario
    nombre = nombres_por_codigo.get(codigo, 'Desconocido')

    # Verificar si la tarjeta está autorizada
    if autorizado_por_codigo.get(codigo, False):
        resultado = 'APROBADO'
    else:
        resultado = 'DENEGADO'

    # Registrar evento
    log.append({
        'codigo': codigo,
        'nombre': nombre,
        'hora': hora,
        'estatus': nuevo_estado,
        'resultado': resultado
    })

    return f"UID {codigo} registrado con estatus {nuevo_estado}"

@app.route('/autorizaciones', methods=['GET', 'POST'])
def autorizaciones():
    if request.method == 'POST':
        # Al recibir la solicitud de autorización o denegación
        codigo = request.form.get('uid')
        autorizacion = request.form.get('autorizado') == 'true'

        # Cambiar el estado de autorización de la tarjeta
        autorizado_por_codigo[codigo] = autorizacion

    return render_template('autorizaciones.html', nombres_por_codigo=nombres_por_codigo, autorizado_por_codigo=autorizado_por_codigo)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
