import ddtrace.auto
import logging
import os
from ddtrace import patch

import requests
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://{uname}:{passwd}@{host}/{dbname}".format(
    uname=os.environ.get("DB_USER"),
    passwd=os.environ.get("DB_PASSWORD"),
    host=os.environ.get("DB_HOST"),
    dbname=os.environ.get("DB_NAME")
)
POLL_URL = os.environ.get("POLL_URL")
patch(sqlalchemy=True)
patch(requests=True)
ddtrace.config.flask['distributed_tracing_enabled'] = True
ddtrace.config.flask['service_name'] = 'superservice'
ddtrace.config.flask['collect_view_args'] = True
ddtrace.config.flask['trace_signals'] = True
ddtrace.config.requests['service'] = 'superservice-requests'


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
        question = requests.get(POLL_URL+"/api/questions").json()
    except Exception as err:
        app.logger.error("Could not connect to Polls: %s", err)
        question = "Could not connect to Polls: {}".format(err)

    return render_template('index.html', result=result, question=question)


@app.route('/create-service', methods=['POST'])
def create_service():
    name = request.form.get('name')
    endpoint = request.form.get('endpoint')
    service = Service(name=name, endpoint=endpoint)
    db.session.add(service)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/create-question', methods=['POST'])
def create_question():
    question = request.form.get('question')
    answer = request.form.get('answer')
    requests.post(POLL_URL, data={"question": question, "answer": answer})
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
