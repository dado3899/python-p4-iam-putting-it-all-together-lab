#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

@app.before_request
def route_filter():
    bypass_routes = ["signup","login"]
    if request.endpoint not in bypass_routes and not session.get("user_id"):
        return {"Error": "Unauthorized"},401

class Signup(Resource):
    def post(self):
        try:
            data = request.get_json()
            new_user = User(
                username = data["username"],
                bio = data["bio"],
                image_url = data["image_url"]
            )
            new_user.password_hash = data["password"]
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            return new_user.to_dict(rules = ('-recipes','-password_hash')),201
        except Exception as e:
            return {"Error": "Could not make user"},422

class CheckSession(Resource):
    def get(self):
        user = User.query.filter(User.id == session["user_id"]).first()
        return user.to_dict(rules = ('-recipes','-password_hash')),200
            

class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter(User.username == data["username"]).first()
        if user and user.authenticate(data['password']):
            session['user_id'] = user.id
            print(session)
            return user.to_dict(rules = ('-recipes','-password_hash')),200
        else:
            return {"Error": "Not valid username or password"}, 401

class Logout(Resource):
    def delete(self):
        # session.pop('user_id')
        session['user_id'] = None
        return {},204

class RecipeIndex(Resource):
    def get(self):
        ar = Recipe.query.all()
        dr = []
        for recipe in ar:
            dr.append(recipe.to_dict())
        return dr,200
    
    def post(self):
        try:
            data = request.get_json()
            new_recipe = Recipe(
                title = data["title"],
                instructions = data["instructions"],
                minutes_to_complete = data["minutes_to_complete"],
                user_id = session['user_id']
            )
            db.session.add(new_recipe)
            db.session.commit()
            return new_recipe.to_dict(),201
        except:
            return {"Error":"Could not create recipe"},422


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)