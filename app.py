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
autorizaciones_por_codigo = {}

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

# Diccionario que guarda si una tarjeta está autorizada
autorizado_por_codigo = {}

@app.route('/registro', methods=['POST'])
def recibir_datos():
    data = request.get_json()
    if not data or 'uid' not in data:
        return "Datos no válidos", 400

    codigo = data['uid']
    hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    autorizado = autorizado_por_codigo.get(codigo, False)
    nombre = nombres_por_codigo.get(codigo, 'Desconocido')
    ultimo_estado = estado_por_codigo.get(codigo)

    # Lógica para determinar la solicitud
    if autorizado:
        if ultimo_estado is None or ultimo_estado == 'SALIDA':
            nueva_solicitud = 'INGRESO'
            resultado = 'APROBADO'
        elif ultimo_estado == 'INGRESO':
            nueva_solicitud = 'SALIDA'
            resultado = 'APROBADO'
    else:
        # Usuario NO autorizado: la solicitud debe ser la opuesta al último estado
        if ultimo_estado == 'INGRESO':
            nueva_solicitud = 'SALIDA'
        elif ultimo_estado == 'SALIDA':
            nueva_solicitud = 'INGRESO'
        else:
            nueva_solicitud = 'INGRESO'  # Caso inicial
        resultado = 'DENEGADO'

    # Actualizar estado solo si fue APROBADO
    if resultado == 'APROBADO':
        estado_por_codigo[codigo] = nueva_solicitud

    # Registrar el evento
    log.append({
        'codigo': codigo,
        'nombre': nombre,
        'hora': hora,
        'estatus': nueva_solicitud,
        'resultado': resultado
    })

    return f"UID {codigo} registrado con resultado {resultado}"

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
