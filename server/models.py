from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
# id that is an integer type and a primary key.
    id = db.Column(db.Integer, primary_key = True)
# username that is a String type.
    username = db.Column(db.String, unique = True, nullable = False)
# _password_hash that is a String type.
    _password_hash = db.Column(db.String)
# image_url that is a String type.
    image_url = db.Column(db.String)
# bio that is a String type.
    bio = db.Column(db.String)

    recipes = db.relationship('Recipe', back_populates = "user")
    
    serialize_rules = ('-recipes.user',)

    @hybrid_property
    def password_hash(self):
        raise AttributeError("Can't access this")
        # return self._password_hash
    
    @password_hash.setter
    def password_hash(self, password):
        hashed_password = bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash = hashed_password.decode('utf-8')

    def authenticate(self,password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))
    
    @validates('username')
    def validate_username(self,key,value):
        if value:
            return value
        else:
            raise ValueError("Not valid username")

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    
#     id that is an integer type and a primary key.
    id = db.Column(db.Integer, primary_key = True)
    # title that is a String type.
    title = db.Column(db.String, nullable = False)
    # instructions that is a String type.
    instructions = db.Column(db.String)
    # minutes_to_complete that is an Integer type.
    minutes_to_complete = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    user = db.relationship("User", back_populates="recipes")

    serialize_rules = ('-user.recipes',)

    @validates('title')
    def validate_title(self,key,value):
        if value:
            return value
        else:
            raise ValueError("Not valid title")
        
    @validates('instructions')
    def validate_instructions(self,key,value):
        if 50 <= len(value):
            return value
        else:
            raise ValueError("Not valid instructions")