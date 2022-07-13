from flask import Flask, request, jsonify #framework, what everything else sits on
from flask_sqlalchemy import SQLAlchemy #allows sqlalchemy to work in flask, database structuring language
from flask_marshmallow import Marshmallow #allows marshmallow to work in flask, serialization => takes an object from one language and changes it to another
from flask_cors import CORS #gives other programs permission to access your api
import os 

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__)) #defines path to the file on our computer

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, "app.sqlite") #path to database, knows exactly where databse is when we make requests. Allows for a simulated database (sqlite)

db = SQLAlchemy(app) #wraps our app, inheriting from app
ma = Marshmallow(app) #wraps our app
CORS(app) #wraps our app

class Book(db.Model): #inheriting from db class model (SQLAlchemy docs - Declaring Models(https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/))
    id = db.Column(db.Integer, primary_key=True) #defines a column in the book model that is specific to the ID, we will define the data type we want in SQL. When object is set to primary key, it does not need to go in the constructor
    title = db.Column(db.String, nullable=False) #defining properties of our book, nullable allows user to include something or not based on true or false
    author = db.Column(db.String, nullable=False)
    review = db.Column(db.String, nullable=True) #Allows the user to now leave a review, since nullable is true 
    genre = db.Column(db.String, nullable=False) #Tells user they need to include genre, since nullable is false

    def __init__(self, title, author, review, genre): #constructor class, this is how our books will look when created (blueprint), and they will follow the rules we set 
        self.title = title #instance of title
        self.author = author #instance of author 
        self.review = review #instance of review
        self.genre = genre #instance of genre

class BookSchema(ma.Schema): #Schema, part of the serialization process, this is what it will look like when we return a request
    class Meta:
        fields = ('id', 'title', 'author', 'review', 'genre') #providing what we want the end user to see

book_schema = BookSchema() #Instantiating our class
multiple_book_schema = BookSchema(many=True) #allowing schema for more than one book

@app.route('/book/add', methods=['POST']) #creating a route decorator end point ('/book/add')
def add_book(): #happens everytime user sends a request, like a call back function when a request is sent to this end point
    post_data = request.get_json() #broken down what user sends and stores into variables listed below
    title = post_data.get('title')
    author = post_data.get('author')
    review = post_data.get('review')
    genre = post_data.get('genre')

    new_book = Book(title, author, review, genre) #creating our book instance, creates new book object
    db.session.add(new_book) #grabbing current session (current instance) of our databse and adding the new book to the database
    db.session.commit()#committing the changes to actually be done, like sving the changes 

    return jsonify('You have added a new book.') #tells the user they have added a new book 

@app.route('/book/get', methods=['GET']) #receive all the books added to databse
def get_books():
    books = db.session.query(Book).all() #search database until we find what we are looking for
    return jsonify(multiple_book_schema.dump(books)) #using .dump is a method that "dumps" our object into something we can use - The dump() method is used when the Python objects have to be stored in a file.


@app.route('/book/update/<id>', methods=(['PUT', 'PATCH'])) #methods used for updating
def update_book(id):
    post_data = request.get_json() #broken down what user sends and stores into variables listed below
    title = post_data.get('title')
    author = post_data.get('author')
    review = post_data.get('review')
    genre = post_data.get('genre')

    book = db.session.query(Book).filter(Book.id == id).first()
    
    if title != None:   #wrapped in an if statement to allow a "Safety Net" 
        book.title = title  #if a user does not provide an update, we return the previous value
    if author != None:
        book.author = author
    if review != None:
        book.review = review
    if genre != None:
        book.genre = genre

    db.session.commit()
    return jsonify("Your book has been updated")


@app.route('/book/delete/<id>', methods=['DELETE']) #reference instance of the book you want to remove, this is why we used <id>
def remove_book(id): #pass the id into the function parameters
    book = db.session.query(Book).filter(Book.id == id).first() #we have to find, or query, for the book we want to delete, then run a filter to filter out the book that matches the provided ID
    db.session.delete(book) #deleting our instance of book
    db.session.commit() #committing the changes

    return jsonify(f'You have deleted book {id}')

if __name__ == "__main__":  #call instance of our app 
    app.run(debug=True)