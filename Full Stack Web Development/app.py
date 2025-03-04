from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from werkzeug.utils import secure_filename
import random
import string
import time
from datetime import datetime, timedelta
from flask_uploads import UploadSet, configure_uploads, IMAGES
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'  
SENDGRID_API_KEY = 'wwdvgvdscahc'

app.config['UPLOADED_IMAGES_DEST'] = 'uploads/images'
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads/photos'

if not os.path.exists(app.config['UPLOADED_IMAGES_DEST']):
    os.makedirs(app.config['UPLOADED_IMAGES_DEST'])

if not os.path.exists(app.config['UPLOADED_PHOTOS_DEST']):
    os.makedirs(app.config['UPLOADED_PHOTOS_DEST'])

images = UploadSet('images', IMAGES)
photos = UploadSet('photos', IMAGES)

configure_uploads(app, images)
configure_uploads(app, photos)
#patch_request_class(app)

def get_db():
    conn = sqlite3.connect('automotive.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home page with search, categories, and random product
@app.route('/', methods=['GET', 'POST'])
def home():
    conn = get_db()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    random_product = conn.execute('SELECT * FROM products ORDER BY RANDOM() LIMIT 10').fetchone()
    conn.close()

    if request.method == 'POST':
        search_query = request.form['search']
        return redirect(url_for('search', query=search_query))

    logged_in = 'user_id' in session
    return render_template('home.html', logged_in=logged_in, categories=categories, random_product=random_product)

# Updated Login Route with Custom CAPTCHA
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        captcha_answer = request.form['captcha_answer']
        
        # Verify custom CAPTCHA
        if 'captcha_solution' not in session or int(captcha_answer) != session['captcha_solution']:
            flash('Invalid CAPTCHA answer')
            num1, num2 = random.randint(1, 10), random.randint(1, 10)
            session['captcha_solution'] = num1 + num2
            return render_template('login.html', captcha_question=f"What is {num1} + {num2}?")

        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password)).fetchone()
        admin = conn.execute('SELECT * FROM admins WHERE email = ? AND password = ?', (email, password)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session.pop('captcha_solution', None)
            return redirect(url_for('home'))
        elif admin:
            session['admin_id'] = admin['id']
            session.pop('captcha_solution', None)
            return redirect(url_for('admin'))
        else:
            flash('Invalid credentials')
            num1, num2 = random.randint(1, 10), random.randint(1, 10)
            session['captcha_solution'] = num1 + num2
            return render_template('login.html', captcha_question=f"What is {num1} + {num2}?")

    num1, num2 = random.randint(1, 10), random.randint(1, 10)
    session['captcha_solution'] = num1 + num2
    return render_template('login.html', captcha_question=f"What is {num1} + {num2}?")

# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        district = request.form['district']
        state = request.form['state']
        address = request.form['address']
        pincode = request.form['pincode']

        conn = get_db()
        conn.execute('INSERT INTO users (name, email, phone, district, state, address, pincode, profile_image) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                     (name, email, phone, district, state, address, pincode, 'default_profile.png'))
        conn.commit()
        user_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.close()

        token = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        session['temp_user_id'] = user_id
        session['token'] = token
        session['token_time'] = time.time()

        message = Mail(
            from_email='no-reply@automotive.com',
            to_emails=email,
            subject='Set Your Password',
            html_content=f'Click <a href="http://127.0.0.1:5000/set_password/{token}">here</a> to set your password (valid for 5 minutes)')
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)

        flash('Check your email to set your password')
        return redirect(url_for('register'))
    return render_template('register.html')

# Set password
@app.route('/set_password/<token>', methods=['GET', 'POST'])
def set_password(token):
    if 'temp_user_id' not in session or session['token'] != token or (time.time() - session['token_time']) > 300:
        flash('Link expired or invalid')
        return redirect(url_for('register'))

    if request.method == 'POST':
        password = request.form['password']
        conn = get_db()
        conn.execute('UPDATE users SET password = ? WHERE id = ?', (password, session['temp_user_id']))
        conn.commit()
        conn.close()
        session.pop('temp_user_id')
        session.pop('token')
        session.pop('token_time')
        flash('Password set successfully')
        return redirect(url_for('login'))
    return render_template('set_password.html')

# Forgot password
@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user:
            otp = ''.join(random.choices(string.digits, k=6))
            session['reset_email'] = email
            session['otp'] = otp
            session['otp_time'] = time.time()

            message = Mail(
                from_email='no-reply@automotive.com',
                to_emails=email,
                subject='Reset Your Password',
                html_content=f'Your OTP is {otp}. Valid for 5 minutes.')
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)

            flash('OTP sent to your email')
            return redirect(url_for('reset_password'))
        else:
            flash('Email not found')
    return render_template('forgot.html')

# Reset password
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'reset_email' not in session:
        return redirect(url_for('forgot'))

    remaining_time = 300 - (time.time() - session['otp_time']) if 'otp_time' in session else 0
    if remaining_time <= 0:
        flash('OTP expired')
        session.pop('reset_email', None)
        session.pop('otp', None)
        session.pop('otp_time', None)
        return redirect(url_for('forgot'))

    if request.method == 'POST':
        otp = request.form['otp']
        password = request.form['password']

        if otp == session['otp']:
            conn = get_db()
            conn.execute('UPDATE users SET password = ? WHERE email = ?', (password, session['reset_email']))
            conn.commit()
            conn.close()
            session.pop('reset_email')
            session.pop('otp')
            session.pop('otp_time')
            flash('Password reset successfully')
            return redirect(url_for('login'))
        else:
            flash('Invalid OTP')

        if 'resend' in request.form:
            return redirect(url_for('forgot'))
    return render_template('reset_password.html', remaining_time=int(remaining_time))

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Store query in the database
        conn = get_db()
        conn.execute('INSERT INTO queries (name, email, message) VALUES (?, ?, ?)', (name, email, message))
        conn.commit()
        conn.close()

        # Send acknowledgment email to the user
        acknowledgment_message = Mail(
            from_email='no-reply@automotive.com',
            to_emails=email,
            subject='We Received Your Query',
            html_content='Dear {},<br><br>Thank you for reaching out to us! We have received your query:<br><br>"{}"<br><br>We will get back to you soon.<br><br>Best regards,<br>Automotive Shop Team'.format(name, message)
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(acknowledgment_message)

        flash('Your query has been sent successfully!')
        return redirect(url_for('contact'))
    
    logged_in = 'user_id' in session
    return render_template('contact.html', logged_in=logged_in)

# About Us page
@app.route('/about')
def about():
    logged_in = 'user_id' in session
    return render_template('about.html', logged_in=logged_in)

# Admin page
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    queries = conn.execute('SELECT * FROM queries').fetchall()
    users = conn.execute('SELECT * FROM users').fetchall()
    orders = conn.execute('SELECT o.*, u.name, p.name as product_name FROM orders o JOIN users u ON o.user_id = u.id JOIN products p ON o.product_id = p.id').fetchall()
    conn.close()

    return render_template('admin.html', queries=queries, users=users, orders=orders)

# Add category
@app.route('/admin/add_category', methods=['GET', 'POST'])
def add_category():
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        conn = get_db()
        conn.execute('INSERT INTO categories (name) VALUES (?)', (name,))
        conn.commit()
        conn.close()
        flash('Category added successfully')
        return redirect(url_for('admin'))
    return render_template('add_category.html')

# Add product
@app.route('/admin/add_product', methods=['GET', 'POST'])
def add_product():
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    conn.close()

    if request.method == 'POST':
        category_id = request.form['category_id']
        name = request.form['name']
        price = float(request.form['price'])
        rating = float(request.form['rating'])
        discount = float(request.form['discount'])
        stock = int(request.form['stock'])

        conn = get_db()
        conn.execute('INSERT INTO products (category_id, name, price, rating, discount, stock) VALUES (?, ?, ?, ?, ?, ?)',
                     (category_id, name, price, rating, discount, stock))
        conn.commit()
        conn.close()
        flash('Product added successfully')
        return redirect(url_for('admin'))
    return render_template('add_product.html', categories=categories)

# Product page with categories and random product
@app.route('/product/<int:product_id>')
def product(product_id):
    conn = get_db()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    random_product = conn.execute('SELECT * FROM products ORDER BY RANDOM() LIMIT 10').fetchone()
    conn.close()
    if not product:
        flash('Product not found')
        return redirect(url_for('home'))
    logged_in = 'user_id' in session
    return render_template('product.html', product=product, categories=categories, 
                         random_product=random_product, logged_in=logged_in)

# Products page with categories and random product
@app.route('/products/<category>')
def products(category):
    conn = get_db()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    category_data = conn.execute('SELECT * FROM categories WHERE name = ?', (category,)).fetchone()
    random_product = conn.execute('SELECT * FROM products ORDER BY RANDOM() LIMIT 10').fetchone()
    if category_data:
        products = conn.execute('SELECT * FROM products WHERE category_id = ?', (category_data['id'],)).fetchall()
    else:
        products = []
    conn.close()
    logged_in = 'user_id' in session
    return render_template('products.html', products=products, category=category, 
                         categories=categories, random_product=random_product, logged_in=logged_in)

# Add to cart (requires login)
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session:
        flash('Please login to add items to cart')
        return redirect(url_for('login'))
    
    conn = get_db()
    conn.execute('INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)',
                 (session['user_id'], product_id, 1))
    conn.commit()
    conn.close()
    flash('Product added to cart')
    return redirect(request.referrer or url_for('home'))

# Wishlist (requires login)
@app.route('/wishlist', methods=['GET', 'POST'])
def wishlist():
    if 'user_id' not in session:
        flash('Please login to view wishlist')
        return redirect(url_for('login'))

    conn = get_db()
    if request.method == 'POST':
        product_id = request.form['product_id']
        conn.execute('DELETE FROM wishlist WHERE user_id = ? AND product_id = ?', 
                    (session['user_id'], product_id))
        conn.commit()
    
    wishlist_items = conn.execute('SELECT p.*, w.id as wishlist_id FROM wishlist w JOIN products p ON w.product_id = p.id WHERE w.user_id = ?', 
                               (session['user_id'],)).fetchall()
    conn.close()
    return render_template('wishlist.html', wishlist_items=wishlist_items)

# Add to wishlist (requires login)
@app.route('/add_to_wishlist/<int:product_id>', methods=['POST'])
def add_to_wishlist(product_id):
    if 'user_id' not in session:
        flash('Please login to add items to wishlist')
        return redirect(url_for('login'))
    
    conn = get_db()
    exists = conn.execute('SELECT * FROM wishlist WHERE user_id = ? AND product_id = ?', 
                         (session['user_id'], product_id)).fetchone()
    if not exists:
        conn.execute('INSERT INTO wishlist (user_id, product_id) VALUES (?, ?)',
                    (session['user_id'], product_id))
        conn.commit()
        flash('Product added to wishlist')
    else:
        flash('Product already in wishlist')
    conn.close()
    return redirect(request.referrer or url_for('home'))

# Payment page (requires login)
@app.route('/payment/<int:product_id>', methods=['GET', 'POST'])
def payment(product_id):
    if 'user_id' not in session:
        flash('Please login to make a purchase')
        return redirect(url_for('login'))

    conn = get_db()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()

    if request.method == 'POST':
        payment_method = request.form['payment_method']
        if payment_method == 'online':
            card_number = request.form['card_number']
            password = request.form['password']
            if len(card_number) == 16 and password:
                return redirect(url_for('confirm_order', product_id=product_id, payment_method=payment_method))
            else:
                flash('Payment failed')
        elif payment_method == 'cod':
            return redirect(url_for('confirm_order', product_id=product_id, payment_method=payment_method))
    return render_template('payment.html', product=product)

# Order confirmation
@app.route('/confirm_order/<int:product_id>/<payment_method>', methods=['GET', 'POST'])
def confirm_order(product_id, payment_method):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()

    if request.method == 'POST':
        address = request.form['address']
        delivery_date = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')

        conn = get_db()
        conn.execute('INSERT INTO orders (user_id, product_id, quantity, status, delivery_date, payment_method, address) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (session['user_id'], product_id, 1, 'Confirmed', delivery_date, payment_method, address))
        conn.commit()
        conn.close()

        message = Mail(
            from_email='no-reply@automotive.com',
            to_emails=user['email'],
            subject='Order Confirmed',
            html_content=f'Your order for {product["name"]} is confirmed. Delivery expected by {delivery_date}.')
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)

        flash('Order confirmed!')
        return redirect(url_for('my_orders'))
    return render_template('order_confirmation.html', product=product, user=user)

# Profile page with image upload
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        district = request.form['district']
        state = request.form['state']
        address = request.form['address']
        pincode = request.form['pincode']
        
        profile_image = user['profile_image']
        if 'photo' in request.files and request.files['photo'].filename != '':
            filename = photos.save(request.files['photo'])
            profile_image = filename

        conn = get_db()
        conn.execute('UPDATE users SET name = ?, email = ?, phone = ?, district = ?, state = ?, address = ?, pincode = ?, profile_image = ? WHERE id = ?',
                     (name, email, phone, district, state, address, pincode, profile_image, session['user_id']))
        conn.commit()
        conn.close()
        flash('Profile updated successfully')
        return redirect(url_for('profile'))
    return render_template('profile.html', user=user)

# Search operation
@app.route('/search')
def search():
    query = request.args.get('query', '')
    conn = get_db()
    products = conn.execute('SELECT * FROM products WHERE name LIKE ?', (f'%{query}%',)).fetchall()
    conn.close()
    logged_in = 'user_id' in session
    return render_template('search.html', products=products, query=query, logged_in=logged_in)

# My orders
@app.route('/my_orders', methods=['GET', 'POST'])
def my_orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        order_id = request.form['order_id']
        conn = get_db()
        order = conn.execute('SELECT * FROM orders WHERE id = ? AND user_id = ?', (order_id, session['user_id'])).fetchone()
        if order and order['status'] == 'Confirmed':
            conn.execute('UPDATE orders SET status = "Cancelled" WHERE id = ?', (order_id,))
            conn.commit()
            flash('Order cancelled successfully')
        conn.close()
        return redirect(url_for('my_orders'))

    conn = get_db()
    orders = conn.execute('SELECT o.*, p.name as product_name FROM orders o JOIN products p ON o.product_id = p.id WHERE o.user_id = ?', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('my_orders.html', orders=orders)

if __name__ == '__main__':
    app.run(debug=True)