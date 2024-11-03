from flask import Flask, jsonify, request, render_template, redirect, url_for, session
import json
import uuid
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'clave_secreta_para_sesion'

# Función para cargar datos de un archivo JSON, si el archivo no existe, devuelve una lista vacía
def load_data():
    if os.path.exists('data.json'):
        with open('data.json') as f:
            return json.load(f)
    return []

# Función para guardar datos en un archivo JSON
def save_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

# Función para cargar usuarios de un archivo JSON, si el archivo no existe, devuelve una lista vacía
def load_users():
    if os.path.exists('users.json'):
        with open('users.json') as f:
            return json.load(f)
    return []

# Función para guardar usuarios en un archivo JSON
def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)

# Ruta para la página principal (login)
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('data_monitoring'))
    return render_template('login.html')

# Ruta para autenticación de usuario
@app.route('/login', methods=['POST'])
def login():
    users = load_users()
    username = request.form['username']
    password = request.form['password']

    user = next((u for u in users if u["username"] == username), None)
    if user and check_password_hash(user["password"], password):
        session['username'] = username
        return redirect(url_for('data_monitoring'))
    return 'Login failed. Please check your username and password.'

# Ruta para registro de usuario
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        age = request.form['age']
        language = request.form['language']

        if any(u['username'] == username for u in users):
            return 'Username already exists.'
        
        hashed_password = generate_password_hash(password)
        users.append({
            'username': username,
            'password': hashed_password,
            'email': email,
            'age': age,
            'language': language
        })
        save_users(users)
        return redirect(url_for('index'))
    return render_template('register.html')

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

# Ruta para la página de monitoreo de datos (requiere autenticación)
@app.route('/data_monitoring')
def data_monitoring():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('index.html')

# Ruta para la página de filtro de resultados (requiere autenticación)
@app.route('/filter_results')
def filter_results():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('filter_results.html')

# API para obtener todos los datos
@app.route('/api/data', methods=['GET'])
def get_data():
    data = load_data()
    return jsonify(data)

# API para agregar un nuevo dato
@app.route('/api/data', methods=['POST'])
def add_data():
    new_entry = request.json
    new_entry['id'] = str(uuid.uuid4())
    data = load_data()
    data.append(new_entry)
    save_data(data)
    return jsonify(new_entry), 201

# API para filtrar datos con parámetros específicos
@app.route('/api/data/filter', methods=['GET'])
def filter_data():
    data = load_data()
    age = request.args.get('age', type=int)
    sex = request.args.get('sex')
    region = request.args.get('region')
    country = request.args.get('country')
    
    if age is not None:
        data = [d for d in data if d['age'] >= age]
    if sex:
        data = [d for d in data if d['sex'] == sex]
    if region:
        data = [d for d in data if d['region'] == region]
    if country:
        data = [d for d in data if d['country'] == country]
    
    filtered_data = {
        'count': len(data),
        'data': data
    }
    
    # Guardar los datos filtrados para visualización
    with open('filtered_data.json', 'w') as f:
        json.dump(filtered_data, f, indent=4)
    
    return jsonify(filtered_data)

if __name__ == '__main__':
    app.run(debug=True)
