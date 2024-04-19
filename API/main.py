from flask import Flask, request, jsonify, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'
sqldbname = '../db/products.db'

@app.route('/users', methods = ['GET'])
def get_users():
    conn = sqlite3.connect(sqldbname)
    cur = conn.cursor()
    cur.execute("SELECT * FROM Users")
    users = cur.fetchall()
    user_list = []
    for user in users:
        user_list.append({'UserID':user[0],'FirstName': user[1], 'LastName': user[2],
                                             'UserEmail': user[3], 'Password': user[4]})
    return jsonify(user_list)

@app.route('/users/register', methods = ['POST'])
def add_users():
    conn = sqlite3.connect(sqldbname)
    cur = conn.cursor()
    # Get the Department id, name, account, password, tel, location
    FirstName = request.json.get('FirstName')
    LastName = request.json.get('LastName')
    UserEmail = request.json.get('UserEmail')
    Password = request.json.get('Password')

    #Check if Department,Account, Password are valid
    if UserEmail and Password:
        #insert the department into the db
        cur.execute(
            "INSERT INTO Users (FirstName, LastName, UserEmail, Password) VALUES (?, ?, ?, ?)",
            (FirstName, LastName, UserEmail, Password))

        conn.commit()
        #GET the id of inserted department
        UserID = cur.lastrowid
        #Return the id as a JSON response
        return jsonify({'DepartmentID': UserID})
    else:
        return 'Email and Password are required', 400
# Define the route for login


@app.route('/users/login', methods=['POST'])
def api_login():
    UserEmail = request.json.get('UserEmail')
    Password = request.json.get('Password')

    if UserEmail and Password:
        if check_exists(UserEmail, Password):
            session['UserEmail'] = UserEmail
            return jsonify({'success': True, 'message': 'Login successful'}), 200
        else:
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
    else:
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400

def check_exists(UserEmail, Password):
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()

    sqlcommand = "SELECT * FROM Users WHERE UserEmail = ? AND Password = ?"
    cursor.execute(sqlcommand, (UserEmail, Password))
    data = cursor.fetchall()

    if len(data) > 0:
        result = True
    else:
        result = False

    conn.close()
    return result

@app.route('/products', methods = ['GET'])
def get_products():
    conn = sqlite3.connect(sqldbname)
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    products=cur.fetchall()
    product_list = []
    for product in products:
        product_list.append({'id': product[0], 'title':product[1], 'price':product[2]})
    return jsonify(product_list)

# @app.route('/products/search', methods = ['POST'])
# def search_product():
#     conn = sqlite3.connect(sqldbname1)
#     cur = conn.cursor()
#     search_text = request.json.get('search_text')
#     if search_text:
#         cur.execute("SELECT * FROM products WHERE title = ? ", (search_text,))
#         data = cur.fetchall()
#         conn.close()
#         return jsonify(data)
#     else:
#         return jsonify({"error": "search text are required"})

# @app.route('/products/add', methods = ['POST'])
# def add_to_cart():
#     id = request.json.get('id')
#     quantity = request.json.get('quantity')
#
#     conn = sqlite3.connect(sqldbname1)
#     cur = conn.cursor()
#     cur.execute("SELECT title, price from products where id = ?", id)
#     product = cur.fetchone()
#     conn.close()
#     product_dict = {
#         "id": id,
#         "title": product[1],
#         "price": product[2]
#     }
#     cart = session.get("cart", [])
#     found = False
#     for item in cart:
#         if item["id"] == id:
#             item['quantity'] += quantity
#             found = True
#             break
#     if not found:
#         cart.append(product_dict)
#     session["cart"] = cart
#     return jsonify(cart)
@app.route('/products/<int:id>', methods = ['GET'])
def ao_clb(id):
    conn = sqlite3.connect(sqldbname)
    cur = conn.cursor()
    cur.execute("SELECT * FROM products where id = ?", (id,))
    product = cur.fetchone()
    if product:
        product_dict = {'id': product[0], 'title': product[1], 'price': product[2] }
        return jsonify(product_dict)
    else:
        return "product not found", 404



if __name__ == '__main__':
    app.run(debug=True)

