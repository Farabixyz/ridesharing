from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError 
from datetime import datetime 
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship







app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fuel_app.db'

db = SQLAlchemy(app)

# User model for the database
class User(db.Model):
    __tablename__ = 'users'  # Explicit table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(50), nullable=False)

    orders = db.relationship('FuelOrder', back_populates='user')

# Driver Model
class Driver(db.Model):
    __tablename__ = 'drivers'  # Explicit table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    vehicle_number = db.Column(db.String(50), nullable=True)

    assigned_orders = db.relationship('FuelOrder', back_populates='driver')

#fff
class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    license_plate = db.Column(db.String(50), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Fixed here

    user = db.relationship('User', backref=db.backref('vehicles', lazy=True))
    
    def __repr__(self):
        return f'<Vehicle {self.make} {self.model} {self.year}>'
    
class FuelOrder(db.Model):
    __tablename__ = 'fuel_orders'
    id = db.Column(db.Integer, primary_key=True)
    fuel_type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), default='Pending')
    accepted_by = db.Column(db.String(150), nullable=True)  # New field

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=True)

    user = db.relationship('User', back_populates='orders', foreign_keys=[user_id])
    driver = db.relationship('Driver', back_populates='assigned_orders', foreign_keys=[driver_id])


    def __init__(self, user_id, fuel_type, quantity, total_price, address, status="Pending"):
        self.user_id = user_id
        self.fuel_type = fuel_type
        self.quantity = quantity
        self.total_price = total_price
        self.address = address
        self.status = status

# Initialize the Database
with app.app_context():
    db.drop_all()  # Drop all tables to avoid conflicts
    db.create_all()  # Create tables with the updated schema
    print("Database tables created successfully!")



    # Updated __init__ to accept status
    def __init__(self, user_id, fuel_type, quantity, fuel_station_address, total_price, status="Pending"):
        self.user_id = user_id
        self.fuel_type = fuel_type
        self.quantity = quantity
        self.fuel_station_address = fuel_station_address
        self.total_price = total_price
        self.status = status  # Allow status to be passed or default to "Pending"



# Home page redirects to login
@app.route('/')
def home():
    return render_template('home.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Query the user from the database
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            # Store the username in session
            session['username'] = user.username
            session['role'] = user.role  # Store the user's role in session
            
            # Redirect based on role
            if user.role == 'user':
                return redirect(url_for('dashboard'))
            elif user.role == 'driver':
                return redirect(url_for('dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')


# Sign-up route
@app.route('/signup', methods=['GET', 'POST'])

def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        role = request.form['role']
        
        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
        elif User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
        else:
            # Create a new user
            new_user = User(username=username, password=hashed_password, email=email, phone=phone, role=role)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('signup.html')



@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()

        if request.method == 'POST':
            # Get the updated data from the form
            email = request.form['email']
            phone = request.form['phone']
            
            # Update the user's information
            user.email = email
            user.phone = phone

            # Commit the changes to the database
            db.session.commit()

            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))

        # Render the profile page with the current user details
        return render_template('profile.html', user=user)

    else:
        flash('Please log in to access your profile.', 'info')
        return redirect(url_for('login'))

@app.route('/view_profile')
def view_profile():
    if 'username' in session:
        # Fetch the user data from the database based on the username in the session
        user = User.query.filter_by(username=session['username']).first()
        
        if user:
            return render_template('view_profile.html', user=user)
        else:
            flash('User not found.', 'error')
            return redirect(url_for('login'))
    else:
        flash('Please log in to view your profile.', 'info')
        return redirect(url_for('login'))

# Dashboard route (requires login)
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('You need to log in first.', 'info')
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()

    if user.role == 'driver':
        # Fetch orders that are Pending (not yet assigned to any driver) 
        pending_orders = FuelOrder.query.filter(
            (FuelOrder.status == 'Pending') | (FuelOrder.driver_id == user.id)
        ).all()

        return render_template(
            'dashboard_driver.html',
            driver=user,
            pending_orders=pending_orders
        )

    elif user.role == 'user':
        return render_template('dashboard_user.html', user=user)
    elif user.role == 'admin':
        return render_template('dashboard_admin.html', user=user)
    else:
        flash('Invalid user role.', 'error')
        return redirect(url_for('logout'))









@app.route('/register_vehicle', methods=['GET', 'POST'])
def register_vehicle():
    if 'username' in session and session['role'] == 'driver':
        if request.method == 'POST':
            # Retrieve form data
            vehicle_make = request.form['make']
            vehicle_model = request.form['model']
            vehicle_year = request.form['year']
            vehicle_license_plate = request.form['license_plate']
            user_id = User.query.filter_by(username=session['username']).first().id

            # Try to create a new vehicle entry
            try:
                new_vehicle = Vehicle(make=vehicle_make, model=vehicle_model, year=vehicle_year,
                                      license_plate=vehicle_license_plate, user_id=user_id)
                db.session.add(new_vehicle)
                db.session.commit()

                flash('Vehicle registered successfully!', 'success')
                return redirect(url_for('dashboard'))  # Redirect to the driver dashboard
            except IntegrityError:
                db.session.rollback()  # Rollback the transaction if there's a duplicate error
                flash('This license plate is already registered. Please use a different license plate.', 'error')
                return redirect(url_for('register_vehicle'))

        return render_template('register_vehicle.html')
    else:
        flash('You must be a driver to register a vehicle.', 'error')
        return redirect(url_for('login'))  # Redirect to login if not a driver

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/order_fuel', methods=['GET', 'POST'])
def order_fuel():
    if 'username' not in session:
        flash("Please log in to place an order.", "error")
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        # Retrieve form data
        fuel_type = request.form['fuel_type']
        quantity = float(request.form['quantity'])
        fuel_station_address = request.form['address']  # Get fuel station address

        # Validation: Quantity must be at least 3 liters
        if not fuel_type or quantity < 3:
            flash("Please select a fuel type and order at least 3 liters of fuel.", "error")
            return redirect(url_for('order_fuel'))

        # Calculate total price
        price_per_litre = 120
        total_price = quantity * price_per_litre

        # Create and save the new FuelOrder
        new_order = FuelOrder(
            user_id=user.id,
            fuel_type=fuel_type,
            quantity=quantity,
            address=fuel_station_address,
            total_price=total_price,
            status="Pending"  # Default status
        )

        db.session.add(new_order)
        db.session.commit()

        # Flash success message
        flash(f"Order placed successfully! Total Price: {total_price:.2f} tk", "success")
        return redirect(url_for('dashboard'))

    return render_template('order_fuel.html')  # Display the fuel order form




# Assuming FuelOrder is already imported and available


# Accept Order Route
@app.route('/accept_order/<int:order_id>', methods=['POST'])
def accept_order(order_id):
    if 'username' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('login'))

    driver = User.query.filter_by(username=session['username'], role='driver').first()
    order = FuelOrder.query.get_or_404(order_id)

    # Update status to 'Accepted' and assign the driver
    if order.status == 'Pending' and order.driver_id is None:
        order.status = 'Accepted'
        order.driver_id = driver.id
        db.session.commit()
        flash(f'Order {order.id} has been accepted!', 'success')
    else:
        flash('Order cannot be accepted. It may already be assigned.', 'warning')

    return redirect(url_for('dashboard'))


#reject order 
@app.route('/reject_order/<int:order_id>', methods=['POST'])
def reject_order(order_id):
    if 'username' not in session:
        flash('You need to log in first.', 'info')
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()
    
    # Check if the user is a driver (optional, depending on your logic)
    if user.role != 'driver':
        flash('You do not have permission to reject orders.', 'error')
        return redirect(url_for('dashboard'))

    # Find the order by ID
    order = FuelOrder.query.get(order_id)
    
    if order:
        # Check if the order is still pending
        if order.status == 'Pending':
            order.status = 'Rejected'
            db.session.commit()
            flash("Order rejected successfully.", 'success')
        else:
            flash("This order cannot be rejected because it is no longer pending.", 'warning')
    else:
        flash("Order not found.", 'error')

    return redirect(url_for('dashboard'))  # Redirect back to the driver dashboard

# Pickup Order
@app.route('/pickup_order/<int:order_id>', methods=['POST'])
def pickup_order(order_id):
    if 'username' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('login'))

    driver = User.query.filter_by(username=session['username'], role='driver').first()
    order = FuelOrder.query.get_or_404(order_id)

    if order.status == 'Accepted' and order.driver_id == driver.id:
        order.status = 'Picked Up'
        db.session.commit()
        flash(f'Order {order.id} has been picked up.', 'success')
    else:
        flash('Order cannot be picked up.', 'warning')

    return redirect(url_for('dashboard'))


# Deliver Order
@app.route('/deliver_order/<int:order_id>', methods=['POST'])
def deliver_order(order_id):
    if 'username' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('login'))

    driver = User.query.filter_by(username=session['username'], role='driver').first()
    order = FuelOrder.query.get_or_404(order_id)

    if order.status == 'Picked Up' and order.driver_id == driver.id:
        order.status = 'Delivered'
        db.session.commit()
        flash(f'Order {order.id} has been delivered.', 'success')
    else:
        flash('Order cannot be delivered.', 'warning')

    return redirect(url_for('dashboard'))


#confirm order 

@app.route('/confirm_order', methods=['POST'])
def confirm_order():
    if 'username' not in session:
        flash('Please log in to place an order.', 'error')
        return redirect(url_for('login'))

    # Extract form data
    fuel_type = request.form['fuel_type']
    quantity = int(request.form['quantity'])
    fuel_station_address = request.form['fuel_station_address']
    total_price = float(request.form['total_price'])

    # Create a new fuel order
    user = User.query.filter_by(username=session['username']).first()
    new_order = FuelOrder(
        user_id=user.id,  # Use logged-in user's ID
        fuel_type=fuel_type,
        quantity=quantity,
        address=fuel_station_address,
        total_price=total_price
    )

    db.session.add(new_order)
    db.session.commit()
    flash('Order confirmed successfully!', 'success')
    return redirect(url_for('user_dashboard'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True) 


