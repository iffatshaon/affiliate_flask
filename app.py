from flask import Flask
from Controller import create_blueprint
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

@app.route("/")
def main():
    return f'Started flask! {os.getenv("PEOPLE")}'

create_blueprint(app)