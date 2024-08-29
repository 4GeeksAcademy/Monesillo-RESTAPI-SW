import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
 from models import db, User, People, Planet, Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/people', methods=['GET'])
def get_all_people():
    people = People.query.all()
    return jsonify([person.serialize() for person in people]), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person_by_id(people_id):
    person = People.query.get(people_id)
    if person:
        return jsonify(person.serialize()), 200
    return jsonify({"error": "Person not found"}), 404

@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    planet = Planet.query.get(planet_id)
    if planet:
        return jsonify(planet.serialize()), 200
    return jsonify({"error": "Planet not found"}), 404

@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    current_user_id = 1
    favorites = Favorite.query.filter_by(user_id=current_user_id).all()
    return jsonify([favorite.serialize() for favorite in favorites]), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    current_user_id = 1
    new_favorite = Favorite(user_id=current_user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify(new_favorite.serialize()), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_person(people_id):
    current_user_id = 1
    new_favorite = Favorite(user_id=current_user_id, people_id=people_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify(new_favorite.serialize()), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    current_user_id = 1
    favorite = Favorite.query.filter_by(user_id=current_user_id, planet_id=planet_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"message": "Favorite planet deleted"}), 200
    return jsonify({"error": "Favorite planet not found"}), 404

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_person(people_id):
    current_user_id = 1
    favorite = Favorite.query.filter_by(user_id=current_user_id, people_id=people_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"message": "Favorite person deleted"}), 200
    return jsonify({"error": "Favorite person not found"}), 404

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
