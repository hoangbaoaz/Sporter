from flask import Flask,url_for, render_template, request, redirect, flash, session
import requests
import sqlite3


app = Flask(__name__)
app.secret_key = "your_secret_key"
base_url = 'http://127.0.0.1:5000/users'
sqldbname = '../db/products.db'

@app.route('/changeToLogin')
def changeToLogin():
    return render_template('login.html')

# hiển thị page detail
@app.route('/seeDetails')
def seeDetails():
    return render_template('returnAndExchange.html')

@app.route('/searchPage')
def searchPage():
    return render_template('SearchWithCSSDataDBAddToCartTable.html')
# chuyển hướng page áo câu lạc bộ
@app.route('/aoClb')
def aoClb():
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE id <= 12')
    products = cursor.fetchall()
    conn.close()
    return render_template('aoCLB.html', products=products)

# lấy thông tin sản phẩm từ database và hiển thị
@app.route('/')
def index():
    # Connect to the database and fetch products
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    conn.close()

    # Check if 'current_user' key exists in the session
    if 'current_user' in session:
        current_username = session['current_user']['name']
    else:
        current_username = ""

    # Render the appropriate template based on the session
    if current_username:
        return render_template('index.html', products=products, search_text="", user_name=current_username)
    else:
        return render_template('SearchWithCSSDataDBAddToCartTable.html', search_text="", user_name="")

@app.route('/search_pr')
def search_pr():
    if 'current_user' in session:
        current_username = session['current_user']['name']
    else:
        current_username = ""
    return render_template(
        'SearchWithCSSDataDBAddToCartTable.html',
        search_text="",
        user_name = current_username)

@app.route('/add', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        FirstName = request.form.get('firstName')
        LastName = request.form.get('lastName')
        Email = request.form.get('emailCreateAccount')
        Password = request.form.get('passwordCreateAccount')

        #Check if Email are valid
        if Email and Password:
            response = requests.post(f'{base_url}/register',
                                     json={'FirstName': FirstName, 'LastName': LastName,'UserEmail': Email, 'Password': Password})
            # check if the response is successful:
            if response.status_code == 200:
                user = response.json()
                flash(f"User added successfully")
                return redirect('/')
            else:
                flash('somthing went wrong. please try again later')
                return render_template('login.html')
        else:
            flash('Email and Password are required')
    else:
        return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        UserEmail = request.form['UserEmail']
        Password = request.form['Password']

        obj_user = get_obj_user(UserEmail, Password)
        if obj_user is not None:
            obj_user = {
                "id": obj_user[0],
                "name": obj_user[1],
                "email": obj_user[2]
            }
            session['current_user'] = obj_user
            # Redirect to the main page after successful login
            return redirect('/')
        else:
            flash('Invalid email or password. Please try again.')

    # Default case: render the login page
    return render_template('login.html')



def check_exists(UserEmail, Password):
    result = False;
    # Khai bao bien de tro toi db
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    sqlcommand = "Select * from users where UserEmail = '"+UserEmail+"' and Password = '"+Password+"'"
    cursor.execute(sqlcommand)
    data = cursor.fetchall()
    print(type(data))
    if len(data)>0:
        result = True
    conn.close()
    return result;

def get_obj_user(UserEmail, Password):
    result = None;
    # Khai bao bien de tro toi db
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    # sqlcommand = "Select * from storages where "
    sqlcommand = "Select * from users where UserEmail =? and Password = ?"
    cursor.execute(sqlcommand,(UserEmail,Password))
    # return object
    obj_user = cursor.fetchone()
    if obj_user is not None:
        result = obj_user
    conn.close()
    return result;
@app.route('/logout')
def logout():
    session.pop('current_user', None)
    # Remove 'username' from the session
    return redirect(url_for('index'))

@app.route('/searchData', methods=['POST'])
def searchData():
    #Get data from Request
    # Check if 'username' key exists in the session
    if 'current_user' in session:
        current_username = session['current_user']['name']
    else:
        current_username = ""
    search_text = request.form['searchInput']
    #Thay bang ham load du lieu tu DB
    product_table = load_data_from_db(search_text)
    print(product_table)
    return render_template(
        'SearchWithCSSDataDBAddToCartTable.html',
                           search_text=search_text,
                           products=product_table,
                           user_name=current_username
                           )

#Load dữ liệu và lọc ra bản ghi phù hợp
def load_data(search_text):
    import pandas as pd
    df = pd.read_csv('gradedata.csv')
    dfX = df
    if search_text != "":
        dfX = df[(df["fname"] == search_text) |
                 (df["lname"] == search_text)]
        print(dfX)
    html_table = dfX.to_html(classes='data',
                             escape=False)
    return html_table

def load_data_from_db(search_text):
        sqldbname = '../db/products.db'
        if search_text != "":
            # Khai bao bien de tro toi db
            conn = sqlite3.connect(sqldbname)
            cursor = conn.cursor()
            sqlcommand = ("Select * from products "
                          "where title like '%")+search_text+ "%'"
            cursor.execute(sqlcommand)
            data = cursor.fetchall()
            conn.close()
            return data

    # Đối với phương thức Search
@app.route('/search', methods=['POST'])
def search():
    # Get data from Request
    search_text = request.form['searchInput']
    return render_template('SearchWithCSSDataDBAddToCartTable.html',
                           search_text=search_text)

@app.route("/cart/add", methods=["POST"])
def add_to_cart():

    #2. Get the product id and quantity from the form
    id = request.form["id"]
    quantity = int(request.form["quantity"])

    #3. get the product name and price from the database
    # or change the structure of shopping cart
    connection = sqlite3.connect(sqldbname)
    cursor = connection.cursor()
    cursor.execute("SELECT title, price, img1 "
                   "FROM products WHERE id = ?",
                   id)
    #3.1. get one product
    product = cursor.fetchone()
    connection.close()

    #4. create a dictionary for the product
    product_dict = {
        "id": id,
        "name": product[0],
        "price": product[1],
        "quantity": quantity,
        "picture": product[2],
    }
    #5. get the cart from the session or create an empty list
    cart = session.get("cart", [])

    #6. check if the product is already in the cart
    found = False
    for item in cart:
        if item["id"] == id:
            #6.1 update the quantity of the existing product
            item["quantity"] += quantity
            found = True
            break

    if not found:
        #6.2 add the new product to the cart
        cart.append(product_dict)
    #7. save the cart back to the session
    session["cart"] = cart

    #8. Print out
    rows = len(cart)
    outputmessage = (f'"Product added to cart successfully!"'
                     f"</br>Current: "+str(rows) + " products"
                     f'</br>Continue Search! <a href="/">Search Page</a>'
                     f'</br>View     Shopping Cart! <a href="/view_cart">ViewCart</a>')
    # return a success message

    return outputmessage
@app.route("/view_cart")
def view_cart():
    # get the cart from the session or create an empty list
    # render the cart.html template and pass the cart
    current_cart = []
    if 'cart' in session:
        current_cart = session.get("cart", [])
    if 'current_user' in session:
        current_username = session['current_user']['name']
    else:
        current_username = ""
    return render_template(
        "cart_update.html",
        carts=current_cart,
        user_name=current_username
    )

@app.route('/update_cart', methods=['POST'])
def update_cart():
    # 1. Get the shopping cart from the session
    cart = session.get('cart', [])
    # 2. Create a new cart to store updated items
    new_cart = []
    # 3. Iterate over each item in the cart
    for product in cart:
        product_id = str(product['id'])
        # 3.1 If this product has a new quantity in the form data
        if f'quantity-{product_id}' in request.form:
            quantity = int(request.form[f'quantity-{product_id}'])
            # If the quantity is 0 or this is a delete field, skip this product
            if quantity == 0 or f'delete-{product_id}' in request.form:
                continue
            # Otherwise, update the quantity of the product
            product['quantity'] = quantity
        # 3.2 Add the product to the new cart
        new_cart.append(product)
    # 4. Save the updated cart back to the session
    session['cart'] = new_cart
    # 5.Redirect to the shopping cart page (or wherever you want)
    return redirect(url_for('view_cart'))
@app.route('/proceed_cart', methods=['POST'])
def proceed_cart():
    # 1. Retrieve the user ID from the session:
    if 'current_user' in session:
        user_id = session['current_user']['id']
        user_email = session['current_user']['email']
    else:
        user_id = 0
        user_email = "";
    # 2. Get the shopping cart from the session
    current_cart = []
    if 'cart' in session:
        shopping_cart  = session.get("cart", [])
    # 3.: Save Order Information to the "order" Table
    # Establish a database connection

    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    # Define the order information (Create a new form)
    user_address = "User Address"  # Replace this with the actual address from the session
    user_mobile = "User Mobile"  # Replace this with the actual mobile number from the session
    purchase_date = "2023-10-10"  # Replace this with the actual purchase date
    ship_date = "2023-10-15"  # Replace this with the actual ship date
    status = 1  # Replace this with the actual status (e.g., processing, shipped, etc.)
    # Insert the order into the "order" table
    cursor.execute('''
        INSERT INTO "order" (UserID, UserEmail, UserAddress,
        UserPhone, PurchaseDate, ShipDate, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, user_email, user_address,
          user_mobile, purchase_date, ship_date, status))
    # 4. Get the ID of the inserted order
    order_id = cursor.lastrowid
    print(order_id)
    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    #5: Save Order Details to the "order_details" Table
    # Establish a new database connection (or reuse the existing connection)
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    # Insert order details into the "order_details" table
    for product in shopping_cart:
        product_id = product['id']
        price = product['price']
        quantity = product['quantity']
        cursor.execute('''
            INSERT INTO order_details (order_id, product_id, price, quantity)
            VALUES (?, ?, ?, ?)
        ''', (order_id, product_id, price, quantity))
    # 6. Commit the changes and close the connection
    conn.commit()
    conn.close()
    # 7. To remove the current_cart from the session
    if 'cart' in session:
        current_cart = session.pop("cart", [])
    else:
        print("No current_cart in session.")
    #Call to orders/order_id
    order_url = url_for('orders', order_id=order_id, _external=True)
    return f'Redirecting to order page: <a href="{order_url}">{order_url}</a>'

@app.route('/orders/', defaults={'order_id': None}, methods=['GET'])
@app.route('/orders/<int:order_id>/', methods=['GET'])
def orders(order_id):
    #if 'current_user' in session:
    #    user_id = session['current_user']['id']
    user_id = session.get('current_user', {}).get('id')
    if user_id:
        conn = sqlite3.connect(sqldbname)
        cursor = conn.cursor()
        if order_id is not None:
            cursor.execute('SELECT * FROM "order" WHERE id = ? AND user_id = ?', (order_id, user_id))
            order = cursor.fetchone()
            cursor.execute('SELECT * FROM order_detail WHERE order_id = ?', (order_id,))
            order_details = cursor.fetchall()
            conn.close()
            return render_template('order_details.html', order=order, order_details=order_details)
        else:
            cursor.execute('SELECT * FROM "order" WHERE user_id = ?', (user_id,))
            user_orders = cursor.fetchall()
            conn.close()
            return render_template('orders.html', orders=user_orders)
    return "User not logged in."


if __name__== '__main__':
    app.run(debug=True, host='127.0.0.1', port='5001')
