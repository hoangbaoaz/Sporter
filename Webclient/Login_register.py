from flask import Flask,url_for, render_template, request, redirect, flash, session
import requests
import sqlite3


app = Flask(__name__)
app.secret_key = "your_secret_key"
base_url = 'http://127.0.0.1:5000/users'
sqldbname = '../db/products.db'

@app.route('/')
def index():
    # Check if 'username' key exists in the session
    if 'current_user' in session:
        current_username = session['current_user']['name']
    else:
        current_username = ""
    return render_template(
        'SearchWithCSSDataDBAddToCartTable.html',
        search_text="",
        user_name = current_username)

@app.route('/get_pr', methods = ['GET'])
def get_pr():
    response = requests.get('http://127.0.0.1:5000/products')
    if response.status_code == 200:
        products = response.json()
        return render_template('user.html', products = products)
    else:
        flash('st went wrong')
    return render_template('user.html')
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
                flash(f"User  added successfully")
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
    # Khi nhận dữ liệu từ hành vi post, sau khi nhận dữ liệu
    # từ session sẽ gọi định tuyến sang trang index
    if request.method == 'POST':
        UserEmail = request.form['UserEmail']
        Password = request.form['Password']
        # Store 'username' in the session
        obj_user = get_obj_user(UserEmail,Password)
        if obj_user is not None:
            obj_user = {
                "id" :obj_user[0],
                "name" : obj_user[1],
                "email": obj_user[2]
            }
            session['current_user'] = obj_user
        return redirect('/')
    # Trường hợp mặc định là vào trang login
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



if __name__== '__main__':
    app.run(debug=True, host='127.0.0.1', port='5001')
