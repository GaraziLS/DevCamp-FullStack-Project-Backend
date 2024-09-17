from flask import Flask, logging, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import os


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')

CORS(app, resources={r"/*": {"origins": "https://garazils.github.io"}}, supports_credentials=True)
db = SQLAlchemy(app)
ma = Marshmallow(app)


# User table
class User(db.Model):
    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_name = db.Column(db.String(30), unique=True, nullable=False)
    user_email = db.Column(db.String(50), unique=False, nullable=False)
    user_password = db.Column(db.String(100), unique=False, nullable=False)

    def __init__(self, user_name, user_email, user_password):
        self.user_name = user_name
        self.user_email = user_email
        self.user_password = user_password

# Item table
class Item(db.Model):
    item_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    item_title = db.Column(db.String(100), unique=False)
    item_category = db.Column(db.String(10), unique=False)
    item_content = db.Column(db.UnicodeText, unique=False)
    item_user_id = db.Column(db.Integer, ForeignKey('user.user_id'))

    def __init__(self, item_title, item_category, item_content):
        self.item_title = item_title
        self.item_category = item_category
        self.item_content = item_content



# Schemas
class UserSchema(ma.Schema):
    class Meta:
        fields = ("user_id", "user_name", "user_email", "user_password")

user_schema = UserSchema()
users_schema = UserSchema(many=True)

# Item schema

class ItemSchema(ma.Schema):
    class Meta:
        fields = ("item_id", "item_title", "item_category", "item_content")

item_schema = ItemSchema()
items_schema = ItemSchema(many=True)

# Route to get the root url

# Root route
@app.route('/')
def home():
    return "Server is up and running!", 200

# Route to create a new item

@app.route("/create", methods=['POST', 'OPTIONS'])
def add_item():
    if request.method == 'OPTIONS':
        # Handle the preflight request
        response = jsonify({'status': 'preflight successful'})
        response.headers.add('Access-Control-Allow-Origin', 'https://garazils.github.io')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response, 200
    
    if request.method == 'POST':
        title = request.form.get("Item[item_title]")
        category = request.form.get("Item[item_category]")
        content = request.form.get("Item[item_content]")

        new_item_instance = Item(title, category, content)

        db.session.add(new_item_instance)
        db.session.commit()

        item = Item.query.get(new_item_instance.item_id)
        return item_schema.jsonify(item)

# Route to sign up a new account

@app.route("/signup", methods=['POST'])
def register_user():
    user_name = request.json["user_name"]
    user_email = request.json["user_email"]
    user_password = request.json["user_password"]

    registered_user_instance = User(user_name, user_email, user_password)

    db.session.add(registered_user_instance)
    db.session.commit()

    user = User.query.get(registered_user_instance.user_id) 

    return user_schema.jsonify(user)

@app.route("/login", methods=["POST", "OPTIONS"])
def user_login():
    if request.method == 'OPTIONS':
        # Handle the preflight request
        response = jsonify({'status': 'preflight successful'})
        response.headers.add('Access-Control-Allow-Origin', 'https://garazils.github.io')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response, 200
    
    if request.method == 'POST':
        # Handle the actual POST request
        user_name = request.json["user_name"]
        user_password = request.json["user_password"]
        user = User.query.filter_by(user_name=user_name).first()

        if user and user.user_password == user_password:
            response = jsonify({'message': 'Login successful'})
            response.headers.add('Access-Control-Allow-Origin', 'https://garazils.github.io')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response, 200
        else:
            response = jsonify({"Warning": "Wrong username or password"})
            response.headers.add('Access-Control-Allow-Origin', 'https://garazils.github.io')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response, 401
    
## TODO: Refactor this preflight thing, if possible.

## TODO: Create a function that checks if a username is available or not when signing up.

# Route to get all the items

@app.route("/tables", methods=['GET'])
def get_items():
    all_items = Item.query.all()
    result = items_schema.dump(all_items)
    return jsonify(result)

## Route to get all the users

@app.route("/users", methods=['GET'])
def get_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result)

# Route to get a single item

@app.route("/tables/<id>", methods=['GET'])
def get_item(id):
    single_item = Item.query.get(id)
    return item_schema.jsonify(single_item)

# Route to get a single user

@app.route("/users/<id>", methods=['GET'])
def get_user(id):
    single_user = User.query.get(id)
    return user_schema.jsonify(single_user)

# Route to update an item

@app.route("/tables/<id>", methods=["PUT", "OPTIONS"])
def item_update(id):
    if request.method == 'OPTIONS':
        # Handle the preflight request
        response = jsonify({'status': 'preflight successful'})
        response.headers.add('Access-Control-Allow-Origin', 'https://garazils.github.io')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'PUT, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response, 200
    
    if request.method == 'PUT':
        update_item_query = Item.query.get(id)
        item_title = request.form.get("Item[item_title]")
        item_category = request.form.get("Item[item_category]")
        item_content = request.form.get("Item[item_content]")

        update_item_query.item_title = item_title
        update_item_query.item_category = item_category
        update_item_query.item_content = item_content

        db.session.commit()
        return item_schema.jsonify(update_item_query)

# Route to delete an item

@app.route("/tables/<id>", methods=["DELETE"])
def delete_item(id):
    item = Item.query.get(id)
    db.session.delete(item)
    db.session.commit()
    return "Item was deleted"

# Route to delete a user

@app.route("/users/<id>", methods=["DELETE"])
def delete_user(id):
    item = User.query.get(id)
    db.session.delete(item)
    db.session.commit()
    return "User account was deleted"


def init_db():
    db.create_all()

if __name__ == '__main__':
    with app.app_context(): 
        init_db()  
    app.run(debug=True)