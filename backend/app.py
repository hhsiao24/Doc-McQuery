# app.py
from flask import Flask

from .config.db import DbInitializer

app = Flask(__name__)

db = DbInitializer()
connection = db.get_connection()


@app.route("/health")
def hello():
    return "The server has been eating apples 🍎!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
