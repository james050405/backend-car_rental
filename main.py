from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask import jsonify
from flask_httpauth import HTTPBasicAuth
import os
from flask_login import LoginManager, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='templates')
app.secret_key = 'b_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///carrental.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.debug = True

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

def index():
    return render_template('index.html')

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    carName = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    seats = db.Column(db.Integer, nullable=False)
    fuel = db.Column(db.String(20), nullable=False)
    transmission = db.Column(db.String(20), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    engineDisplacement = db.Column(db.Integer, nullable=False)
    enginePower = db.Column(db.String(20), nullable=False)
    consumption = db.Column(db.String(20), nullable=False)

def create_app_context():
    with app.app_context():
        initialize_database()

def initialize_database():
    db.create_all()
    if not Car.query.first():
        new_car = Car(carName='Audi A4', model='A4', seats=5, fuel='Petrol', transmission='Automatic', year=2020, price=30000, engineDisplacement=1984, enginePower='150hp', consumption='7.4l/100km')
        db.session.add(new_car)
        db.session.commit()
    cars = Car.query.all()
    for car in cars:
        print(car.carName)

cars = Car.query.all()
for car in cars:
    print(car.carName)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    driverLicenseNumber = db.Column(db.String(20), nullable=False)
    street = db.Column(db.String(50), nullable=False)
    houseNumber = db.Column(db.String(10), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    zipCode = db.Column(db.String(10), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    carId = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    start = db.Column(db.String(10), nullable=False)
    end = db.Column(db.String(10), nullable=False)
    pickupLocation = db.Column(db.String(50), nullable=False)

api = Api(app)


user_admin = {
    "admin": {"password_hash": "hash_of_password"}
}

class Login(Resource):  
    user_admin = {'admin': {'password_hash': generate_password_hash('Admin12345')}}

    @login_manager.user_loader
    def load_user(user_id):
        user_admin = Login.User()
        user_admin.id = user_id
        return user_admin
        
    @staticmethod
    def authenticate(username, password):
        user = Login.user_admin.get(username)
        if user and check_password_hash(user['password_hash'], password):
            user_obj = Login.User()
            user_obj.id = username
            login_user(user_obj)
            return user_obj
        return None

class Logout(Resource):
    @login_required
    def get(self):
        logout_user()
        return redirect(url_for('index'))

class Cars(Resource):
    def get(self):
        cars = Car.query.all()
        car_list = []
        for car in cars:
            car_data = {
                'id': car.id,
                'carName': car.carName,
                'model': car.model,
                'seats': car.seats,
                'fuel': car.fuel,
                'transmission': car.transmission,
                'year': car.year,
                'price': car.price,
                'engineDisplacement': car.engineDisplacement,
                'enginePower': car.enginePower,
                'consumption': car.consumption
            }
            car_list.append(car_data)
        return jsonify(car_list)

class CarDetails(Resource):
    def get(self, car_id):
        car = Car.query.filter_by(id=car_id).first()
        if car:
            car_data = {
                'id': car.id,
                'carName': car.carName,
                'model': car.model,
                'seats': car.seats,
                'fuel': car.fuel,
                'transmission': car.transmission,
                'year': car.year,
                'price': car.price,
                'engineDisplacement': car.engineDisplacement,
                'enginePower': car.enginePower,
                'consumption': car.consumption
            }
            return jsonify(car_data)
        else:
            return jsonify({'message': 'Car not found'}), 404

class Orders(Resource):
    def get(self):
        orders = Order.query.all()
        order_list = []
        for order in orders:
            order_data = {
                'id': order.id,
                'name': order.name,
                'surname': order.surname,
                'email': order.email,
                'phone': order.phone,
                'driverLicenseNumber': order.driverLicenseNumber,
                'street': order.street,
                'houseNumber': order.houseNumber,
                'city': order.city,
                'zipCode': order.zipCode,
                'country': order.country,
                'carId': order.carId,
                'price': order.price,
                'start': order.start,
                'end': order.end,
                'pickupLocation': order.pickupLocation
            }
            order_list.append(order_data)
        return jsonify(order_list)
    
class Filters(Resource):
    def get(self):
        pass

class AdminPanel(Resource):
    @classmethod
    @app.route("/panel", methods=['GET', 'POST'], endpoint="admin_login")    
    def admin_login(cls):
        if request.method == 'POST':            
            username = request.form['username']
            password = request.form['password']
            if Login.authenticate(username, password):
                return redirect(url_for('admin'))
            else:
                return render_template('login.html', message="Neplatné přihlašovací údaje")
        else:
            return render_template("login.html")

    
    @classmethod
    @app.route("/panel", methods = ["GET"], endpoint = "admin_panel")
    @login_required    
    def admin_panel(cls):
        return render_template('admin_panel.html')


class Panel(Resource):
    @classmethod
    @app.route("/panel")
    @login_required
    def panel(cls):
        return render_template('admin_panel.html')
    
    @classmethod
    @app.route("/panel", methods=['GET', 'POST'])
    def login_panel(cls):
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            if Login.authenticate(username, password):
                return redirect(url_for('panel'))
            else:
                return render_template('login.html', message="Neplatné přihlašovací údaje")
        else:
            return render_template("login.html")

cars = Car.query.all()
for car in cars:
    print(car.carName)


api.add_resource(Cars, '/getCars')
api.add_resource(CarDetails, '/getCars/<int:car_id>')
api.add_resource(Orders, '/orders')
api.add_resource(Filters, '/getFilters')
api.add_resource(Panel, '/panel')
api.add_resource(AdminPanel, '/admin')

if __name__ == "__main__":
    create_app_context()    
    app.run(host='127.0.0.1', debug=True, port=60000)