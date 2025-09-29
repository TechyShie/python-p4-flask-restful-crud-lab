#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from sqlalchemy.exc import IntegrityError

from models import db, Plant

app = Flask(__name__)

# Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Init DB + Migration
db.init_app(app)
migrate = Migrate(app, db)

# API
api = Api(app)


# ---------- ROUTES ---------- #
class Plants(Resource):
    def get(self):
        """Fetch all plants"""
        plants = [plant.to_dict() for plant in Plant.query.all()]
        return make_response(plants, 200)

    def post(self):
        """Create a new plant"""
        data = request.get_json()

        try:
            new_plant = Plant(
                name=data.get('name'),
                image=data.get('image'),
                price=data.get('price'),
                is_in_stock=data.get('is_in_stock', True)  # default True
            )
            db.session.add(new_plant)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return make_response({"error": "Plant could not be created"}, 400)

        return make_response(new_plant.to_dict(), 201)


class PlantByID(Resource):
    def get(self, id):
        """Fetch plant by ID"""
        plant = Plant.query.filter_by(id=id).first()
        if not plant:
            return make_response({"error": "Plant not found"}, 404)
        return make_response(plant.to_dict(), 200)

    def patch(self, id):
        """Update plant by ID"""
        plant = Plant.query.filter_by(id=id).first()
        if not plant:
            return make_response({"error": "Plant not found"}, 404)

        data = request.get_json()
        if "name" in data:
            plant.name = data["name"]
        if "image" in data:
            plant.image = data["image"]
        if "price" in data:
            plant.price = data["price"]
        if "is_in_stock" in data:
            plant.is_in_stock = data["is_in_stock"]

        db.session.commit()
        return make_response(plant.to_dict(), 200)

    def delete(self, id):
        """Delete plant by ID"""
        plant = Plant.query.filter_by(id=id).first()
        if not plant:
            return make_response({"error": "Plant not found"}, 404)

        db.session.delete(plant)
        db.session.commit()
        # ✅ Return nothing + 204 to satisfy tests
        return make_response('', 204)


# Register resources
api.add_resource(Plants, '/plants')
api.add_resource(PlantByID, '/plants/<int:id>')


# ---------- MAIN ---------- #
if __name__ == '__main__':
    app.run(port=5555, debug=True)
