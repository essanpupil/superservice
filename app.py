import os

from flask import Flask, render_template
import logging
import urllib
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://{uname}:{passwd}@{host}/{dbname}".format(
    uname=os.environ.get("DB_USER"),
    passwd=os.environ.get("DB_PASSWORD"),
    host=os.environ.get("DB_HOST"),
    dbname=os.environ.get("DB_NAME")
)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)
class Service(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    endpoint: Mapped[str]


if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


@app.route('/healthcheck')
def healthcheck():
    db.session.execute(db.select(Service).order_by(Service.name)).scalars()
    return "OK", 200


@app.route('/')
def index():
    result = db.session.execute(db.select(Service).order_by(Service.name)).scalars()
    try:
        question = urllib.request.urlopen("http://internal-polls-1382146748.ap-southeast-1.elb.amazonaws.com:8000").read()
    except Exception as err:
        app.logger.error("Could not connect to Polls: %s", err)
        question = "Could not connect to Polls: {}".format(err)

    return render_template('index.html', result=result, question=question)


@app.route('/create-service-table')
def create_service():
    result = db.session.execute(db.select(Service).order_by(Service.name)).scalars()
    return render_template('index.html', result=result)


@app.route('/create-question-table')
def create_question():
    try:
        question = urllib.request.urlopen("http://internal-polls-1382146748.ap-southeast-1.elb.amazonaws.com:8000/create-question-table").read()
    except Exception as err:
        app.logger.error("Could not connect to Polls: %s", err)
        question = "Could not connect to Polls: {}".format(err)

    return render_template('index.html', result=question)


@app.route('/polls')
def polls():
    return render_template('polls.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
