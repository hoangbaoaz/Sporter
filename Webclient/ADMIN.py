from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Felix Pham'

# Check if the database file exists, if not, create it
db_file = '../db/products.db'
if not os.path.exists(db_file):
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE products (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      title TEXT NOT NULL,
                      price TEXT NOT NULL,
                      img1 TEXT NOT NULL,
                      )''')
    connection.commit()
    connection.close()

def get_db_connection():
    connection = sqlite3.connect(db_file)
    connection.row_factory = sqlite3.Row
    return connection

@app.route('/')
def index():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM products')
    storages = cursor.fetchall()
    connection.close()
    return render_template('Admin/Storages/index.html', storages=storages)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']
        img = request.form['img1']

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('''INSERT INTO products (title, price, img1)
                          VALUES (?, ?, ?)''', (title, price, img,))
        connection.commit()
        connection.close()

        flash('Storage added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('Admin/Storages/add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM products WHERE id = ?', (id,))
    storage = cursor.fetchone()
    connection.close()

    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']
        img = request.form['img']

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('''UPDATE products SET title=?, price=?, img1=?
                          WHERE id=?''', (title, price,img, id))
        connection.commit()
        connection.close()

        flash('Storage updated successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('Admin/Storages/edit.html', storage=storage)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM products WHERE id = ?', (id,))
    connection.commit()
    connection.close()

    flash('Storage deleted successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5005)