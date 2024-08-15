from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import os


app = Flask(__name__)


basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')

CORS(app, origins="http://localhost:3000", supports_credentials=True)

@app.before_request
def before_request():
    pass

@app.after_request
def after_request(response):
    return response



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

    def __init__(self, item_title, item_category, item_content, item_user_id):
        self.item_title = item_title
        self.item_category = item_category
        self.item_content = item_content
        self.item_user_id = item_user_id



# Schemas
class UserSchema(ma.Schema):
    class Meta:
        fields = ("user_id", "user_name", "user_email", "user_password")

user_schema = UserSchema()
users_schema = UserSchema(many=True)

# Item schema

class ItemSchema(ma.Schema):
    class Meta:
        fields = ("item_id", "item_title", "item_category", "item_content", "item_user_id")

item_schema = ItemSchema()
items_schema = ItemSchema(many=True)

# Route to create a new item

@app.route("/create", methods=['POST'])
def add_item():
    title = request.json["item_title"]
    category = request.json["item_category"]
    content = request.json["item_content"]
    item_user_id = request.json["item_user_id"]

    new_item_instance = Item(title, category, content, item_user_id)

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

@app.route('/login', methods=['OPTIONS', 'POST'])
def login():
    if request.method == 'OPTIONS':
        # This is the preflight request
        response = jsonify({'status': 'preflight successful'})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response, 200

    # Actual POST request handling
    response = jsonify({'message': 'Login successful'})
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response, 200
def login_user():
    user_name = request.json["user_name"]
    user_password = request.json["user_password"]

    user = User.query.filter_by(user_name=user_name).first()

    if user and user_password == user_password:
        return user_schema.jsonify(user)
    else:
        return jsonify({"Warning": "Wrong username or password "}), 401
    
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

@app.route("/tables/<id>", methods=["PUT"])
def item_update(id):
    update_item_query = Item.query.get(id)
    item_title = request.json["item_title"]
    item_category = request.json["item_category"]
    item_content = request.json["item_content"]
    item_user_id = request.json["item_user_id"]

    update_item_query.item_title = item_title
    update_item_query.item_category = item_category
    update_item_query.item_content = item_content
    update_item_query.item_user_id = item_user_id

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
    app.run(host="localhost", port=5000, debug=True)