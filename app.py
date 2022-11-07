from flask import Flask, jsonify, render_template
from flask_pymongo import PyMongo
import socket
import requests

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://mongo:27017/dev"
mongo = PyMongo(app)
db = mongo.db

@app.route("/")
def index():
    return jsonify(
        message="Welcome to Chuck Norris jokes app!"
    )

@app.route("/get_joke")
def get_all_jokes():
    jokes = db.jokes.find()
    data = []
    for joke in jokes:
        data.append(joke["joke"])
        data.append('<br/>')
    #return (data)
    return render_template("data.html", data=data)

@app.route("/add_joke")
def create_task():
    joke = requests.get('https://api.chucknorris.io/jokes/random').json()['value']
    db.jokes.insert_one({"joke": joke})
    return jsonify(
        message="Joke added successfully!"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
