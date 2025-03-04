import sqlite3

def init_db():
    conn = sqlite3.connect('automotive.db')
    c = conn.cursor()

    # Create tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, email TEXT UNIQUE, phone TEXT, district TEXT, state TEXT, address TEXT, pincode TEXT, password TEXT, profile_image TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE, password TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER, name TEXT, price REAL, rating REAL, discount REAL, stock INTEGER, image_url TEXT,
        FOREIGN KEY(category_id) REFERENCES categories(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, product_id INTEGER, quantity INTEGER, status TEXT, delivery_date TEXT, payment_method TEXT, address TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS queries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT, query_text TEXT, timestamp TEXT
    )''')

    # Insert default admin
    default_admins = [
    ('sandeeppittala124@gmail.com', 'sandeep123'),  # First default admin
    ('sandeeppittala2707@gmail.com', 'sandeep124')  # Second default admin
]
    c.executemany('INSERT OR IGNORE INTO admins (email, password) VALUES (?, ?)', default_admins)

    # Insert categories
    categories = ['Wheels', 'Lights', 'Wipers', 'Swings', 'Tires', 'Window Glasses']
    for category in categories:
        c.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (category,))

    # Product data with image URLs
    products = {
        'Wheels': [
            ('Alloy Wheel 15"', 120.99, 4.5, 10.0, 50, 'https://www.carid.com/images/wheels/alloy-wheel-15.jpg'),
            ('Steel Wheel 16"', 89.50, 4.0, 5.0, 30, 'https://www.tirerack.com/images/steel-wheel-16.jpg'),
            ('Chrome Wheel 17"', 150.00, 4.8, 15.0, 20, 'https://www.wheelhero.com/images/chrome-wheel-17.jpg'),
            ('Matte Black Wheel 18"', 130.75, 4.3, 12.0, 25, 'https://www.discounttire.com/images/matte-black-wheel-18.jpg'),
            ('Racing Wheel 19"', 200.00, 4.9, 20.0, 15, 'https://www.performanceplus.com/images/racing-wheel-19.jpg'),
            ('Off-Road Wheel 20"', 180.25, 4.6, 10.0, 10, 'https://www.4wheelparts.com/images/offroad-wheel-20.jpg'),
            ('Spoke Wheel 15"', 110.00, 4.2, 8.0, 40, 'https://www.autozone.com/images/spoke-wheel-15.jpg'),
            ('Custom Wheel 16"', 140.50, 4.7, 15.0, 35, 'https://www.jegs.com/images/custom-wheel-16.jpg'),
            ('Lightweight Wheel 17"', 125.99, 4.4, 10.0, 45, 'https://www.summitracing.com/images/lightweight-wheel-17.jpg'),
            ('Luxury Wheel 18"', 175.00, 4.8, 18.0, 20, 'https://www.wheelsforless.com/images/luxury-wheel-18.jpg'),
        ],
        'Lights': [
            ('LED Headlight', 45.99, 4.7, 10.0, 100, 'https://www.amazon.com/images/led-headlight.jpg'),
            ('Halogen Bulb', 15.50, 4.0, 5.0, 150, 'https://www.walmart.com/images/halogen-bulb.jpg'),
            ('Fog Light', 35.75, 4.5, 8.0, 80, 'https://www.autozone.com/images/fog-light.jpg'),
            ('Tail Light LED', 50.00, 4.8, 12.0, 60, 'https://www.oreillyauto.com/images/tail-light-led.jpg'),
            ('Interior Light', 20.25, 4.3, 5.0, 90, 'https://www.advanceautoparts.com/images/interior-light.jpg'),
            ('Brake Light', 25.99, 4.6, 10.0, 70, 'https://www.pepboys.com/images/brake-light.jpg'),
            ('Xenon Headlight', 60.00, 4.9, 15.0, 40, 'https://www.carid.com/images/xenon-headlight.jpg'),
            ('Side Marker Light', 12.50, 4.2, 5.0, 120, 'https://www.rockauto.com/images/side-marker-light.jpg'),
            ('Turn Signal LED', 30.00, 4.7, 10.0, 85, 'https://www.ebay.com/images/turn-signal-led.jpg'),
            ('Spotlight', 75.00, 4.8, 20.0, 25, 'https://www.4wheelparts.com/images/spotlight.jpg'),
        ],
        'Wipers': [
            ('Wiper Blade 20"', 15.99, 4.4, 5.0, 200, 'https://www.amazon.com/images/wiper-blade-20.jpg'),
            ('Wiper Blade 22"', 17.50, 4.5, 5.0, 180, 'https://www.walmart.com/images/wiper-blade-22.jpg'),
            ('Rear Wiper 14"', 12.75, 4.3, 5.0, 150, 'https://www.autozone.com/images/rear-wiper-14.jpg'),
            ('Silicone Wiper 24"', 20.00, 4.7, 10.0, 120, 'https://www.oreillyauto.com/images/silicone-wiper-24.jpg'),
            ('Heavy Duty Wiper 26"', 25.99, 4.8, 15.0, 90, 'https://www.advanceautoparts.com/images/heavy-duty-wiper-26.jpg'),
            ('Winter Wiper 18"', 18.25, 4.6, 8.0, 110, 'https://www.pepboys.com/images/winter-wiper-18.jpg'),
            ('Beam Wiper 21"', 22.50, 4.7, 10.0, 130, 'https://www.carid.com/images/beam-wiper-21.jpg'),
            ('Hybrid Wiper 23"', 19.99, 4.5, 5.0, 140, 'https://www.rockauto.com/images/hybrid-wiper-23.jpg'),
            ('Eco Wiper 19"', 14.75, 4.3, 5.0, 160, 'https://www.ebay.com/images/eco-wiper-19.jpg'),
            ('Premium Wiper 25"', 28.00, 4.9, 15.0, 80, 'https://www.discounttire.com/images/premium-wiper-25.jpg'),
        ],
        'Swings': [
            ('Swing Arm Short', 50.00, 4.5, 10.0, 60, 'https://www.amazon.com/images/swing-arm-short.jpg'),
            ('Swing Arm Long', 65.99, 4.6, 12.0, 50, 'https://www.walmart.com/images/swing-arm-long.jpg'),
            ('Adjustable Swing', 75.50, 4.7, 15.0, 40, 'https://www.autozone.com/images/adjustable-swing.jpg'),
            ('Heavy Swing Arm', 80.00, 4.8, 10.0, 30, 'https://www.oreillyauto.com/images/heavy-swing-arm.jpg'),
            ('Light Swing Arm', 45.25, 4.4, 5.0, 70, 'https://www.advanceautoparts.com/images/light-swing-arm.jpg'),
            ('Steel Swing', 70.99, 4.7, 12.0, 45, 'https://www.pepboys.com/images/steel-swing.jpg'),
            ('Aluminum Swing', 60.00, 4.6, 10.0, 55, 'https://www.carid.com/images/aluminum-swing.jpg'),
            ('Custom Swing', 85.75, 4.9, 15.0, 25, 'https://www.rockauto.com/images/custom-swing.jpg'),
            ('Racing Swing', 90.00, 4.8, 20.0, 20, 'https://www.ebay.com/images/racing-swing.jpg'),
            ('Off-Road Swing', 77.50, 4.7, 10.0, 35, 'https://www.4wheelparts.com/images/offroad-swing.jpg'),
        ],
        'Tires': [
            ('All-Season Tire 15"', 80.99, 4.6, 10.0, 100, 'https://www.tirerack.com/images/all-season-tire-15.jpg'),
            ('Winter Tire 16"', 95.50, 4.7, 12.0, 80, 'https://www.discounttire.com/images/winter-tire-16.jpg'),
            ('Summer Tire 17"', 110.00, 4.8, 15.0, 60, 'https://www.walmart.com/images/summer-tire-17.jpg'),
            ('Off-Road Tire 18"', 130.75, 4.7, 10.0, 50, 'https://www.4wheelparts.com/images/offroad-tire-18.jpg'),
            ('Performance Tire 19"', 150.00, 4.9, 20.0, 40, 'https://www.performanceplus.com/images/performance-tire-19.jpg'),
            ('Mud Tire 20"', 140.25, 4.6, 10.0, 45, 'https://www.amazon.com/images/mud-tire-20.jpg'),
            ('Eco Tire 16"', 90.99, 4.5, 5.0, 90, 'https://www.autozone.com/images/eco-tire-16.jpg'),
            ('Touring Tire 17"', 105.50, 4.7, 12.0, 70, 'https://www.oreillyauto.com/images/touring-tire-17.jpg'),
            ('Racing Tire 18"', 160.00, 4.9, 15.0, 30, 'https://www.carid.com/images/racing-tire-18.jpg'),
            ('Truck Tire 19"', 145.75, 4.8, 10.0, 55, 'https://www.pepboys.com/images/truck-tire-19.jpg'),
        ],
        'Window Glasses': [
            ('Front Windshield', 200.00, 4.8, 10.0, 25, 'https://www.safelite.com/images/front-windshield.jpg'),
            ('Rear Windshield', 180.50, 4.7, 10.0, 30, 'https://www.autoglassnow.com/images/rear-windshield.jpg'),
            ('Side Window Left', 90.99, 4.5, 5.0, 50, 'https://www.amazon.com/images/side-window-left.jpg'),
            ('Side Window Right', 90.99, 4.5, 5.0, 50, 'https://www.walmart.com/images/side-window-right.jpg'),
            ('Tinted Windshield', 220.75, 4.9, 15.0, 20, 'https://www.carid.com/images/tinted-windshield.jpg'),
            ('Laminated Glass', 210.00, 4.8, 12.0, 25, 'https://www.autozone.com/images/laminated-glass.jpg'),
            ('Heated Windshield', 250.00, 4.9, 20.0, 15, 'https://www.oreillyauto.com/images/heated-windshield.jpg'),
            ('Curved Glass', 195.25, 4.7, 10.0, 35, 'https://www.pepboys.com/images/curved-glass.jpg'),
            ('UV-Protect Glass', 230.50, 4.8, 15.0, 20, 'https://www.rockauto.com/images/uv-protect-glass.jpg'),
            ('Replacement Glass', 175.99, 4.6, 5.0, 40, 'https://www.ebay.com/images/replacement-glass.jpg'),
        ]
    }

    # Insert products
    for category_name, product_list in products.items():
        c.execute('SELECT id FROM categories WHERE name = ?', (category_name,))
        category_id = c.fetchone()[0]
        for name, price, rating, discount, stock, image_url in product_list:
            c.execute('INSERT OR IGNORE INTO products (category_id, name, price, rating, discount, stock, image_url) VALUES (?, ?, ?, ?, ?, ?, ?)',
                      (category_id, name, price, rating, discount, stock, image_url))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()