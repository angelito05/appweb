from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import os
import conexion as db

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src', 'templates'))

app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'supersecretkey'

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/submit', methods=['POST'])
def submit():
    email = request.form['email']
    password = request.form['password']
    
    if not email or not password:
        flash('Por favor, complete todos los campos')
        return redirect(url_for('register'))
    
    cursor = db.conexion.cursor()
    cursor.execute('''
        INSERT INTO usuario (correo, contraseña) VALUES (%s, %s)
    ''', (email, password))
    db.conexion.commit()
    cursor.close()
    
    flash('Registro exitoso')
    return redirect(url_for('home'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    
    cursor = db.conexion.cursor()
    cursor.execute('''
        SELECT * FROM usuario WHERE correo = %s AND contraseña = %s
    ''', (email, password))
    user = cursor.fetchone()
    cursor.close()
    
    if user:
        session['user_id'] = user[1]
        flash('Inicio de sesión exitoso')
        return redirect(url_for('dashboard'))
    else:
        flash('Correo electrónico o contraseña incorrectos')
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Sesión cerrada correctamente')
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return render_template('dashboard.html')
    else:
        flash('Por favor, inicia sesión primero')
        return redirect(url_for('home'))

@app.route('/register_product')
def register_product():
    if 'user_id' in session:
        return render_template('register_product.html')
    else:
        flash('Por favor, inicia sesión primero')
        return redirect(url_for('home'))

@app.route('/save_product', methods=['POST'])
def save_product():
    if 'user_id' in session:
        user_id = session['user_id']
        nombre_material = request.form['nombre_material']
        categoria = request.form['categoria']
        precio = request.form['precio']
        disponibilidad = request.form['disponibilidad']
        marca_producto = request.form['marca_producto']
        negocio = request.form['negocio']
        
        cursor = db.conexion.cursor()
        cursor.execute('''
            INSERT INTO materiales (nombre_material, categoria, precio, disponibilidad, marca_producto, negocio) 
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (nombre_material, categoria, precio, disponibilidad, marca_producto, negocio))
        db.conexion.commit()
        cursor.close()
        
        flash('Producto registrado correctamente')
        return redirect(url_for('register_product'))
    else:
        flash('Por favor, inicia sesión primero')
        return redirect(url_for('home'))

@app.route('/update_products', methods=['POST'])
def update_products():
    if 'user_id' in session:
        user_id = session['user_id']
        nombre_material = request.form['nombre_material']
        categoria = request.form['categoria']
        precio = request.form['precio']
        disponibilidad = request.form['disponibilidad']
        marca_producto = request.form['marca_producto']
        
        cursor = db.conexion.cursor()
        cursor.execute('''
            UPDATE materiales 
            SET nombre_material = %s, categoria = %s, precio = %s, disponibilidad = %s, marca_producto = %s
            WHERE negocio = %s
        ''', (nombre_material, categoria, precio, disponibilidad, marca_producto, user_id))
        db.conexion.commit()
        cursor.close()
        
        flash('Productos actualizados correctamente')
        return redirect(url_for('register_product'))
    else:
        flash('Por favor, inicia sesión primero')
        return redirect(url_for('home'))

@app.route('/get_products')
def get_products():
    if 'user_id' in session:
        user_id = session['user_id']
        
        cursor = db.conexion.cursor()
        cursor.execute('''
            SELECT nombre_material, categoria, precio, disponibilidad, marca.marca
            FROM materiales,usuario, marca
            WHERE usuario.correo = %s
        ''', (user_id,))
        products = cursor.fetchall()
        cursor.close()
        
        product_list = []
        for product in products:
            product_list.append({
                'nombre_material': product[0],
                'categoria': product[1],
                'precio': product[2],
                'disponibilidad': product[3],
                'marca_producto': product[4]
            })
        
        return jsonify(product_list)
    else:
        flash('Por favor, inicia sesión primero')
        return redirect(url_for('home'))


@app.route('/register_business')
def register_business():
    return render_template('register_business.html')

@app.route('/save_business', methods=['POST'])
def save_business():
    nombre = request.form['nombre_negocio']
    ubicacion = request.form['direccion']
    telefono = request.form['telefono']
    correo = request.form['correo']
    
    if not nombre or not ubicacion or not telefono or not correo:
        flash('Por favor, complete todos los campos')
        return redirect(url_for('register_business'))
    
    cursor = db.conexion.cursor()
    cursor.execute('''
        INSERT INTO proveedor (nombre, ubicacion, telefono, correo) VALUES (%s, %s, %s,%s)
    ''', (nombre, ubicacion, telefono))
    db.conexion.commit()
    cursor.close()
    
    flash('Negocio registrado correctamente')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
