import os

from flask import Flask, render_template
import mysql.connector
import logging
import urllib


config = {
    'user': os.environ.get("DB_USER"),
    'password': os.environ.get("DB_PASSWORD"),
    'host': 'superservice-db.c4avp797njw5.ap-southeast-1.rds.amazonaws.com',
    'database': 'superservice',
    'port': '3306',
    'raise_on_warnings': True
}


app = Flask(__name__)
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


@app.route('/healthcheck')
def healthcheck():
    try:
        cnx = mysql.connector.connect(**config)
    except mysql.connector.Error as err:
        app.logger.error("Could not connect to DB: %s", err)
        return "Could not connect to DB"
    if cnx.is_connected():
        return "OK"


@app.route('/')
def index():
    result = []
    try:
        cnx = mysql.connector.connect(**config)
    except Exception as err:
        app.logger.error("Could not connect to DB: %s", err)
        result = "Could not connect to DB"
        return render_template('index.html', result=result)

    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            cursor.execute("SELECT * FROM service LIMIT 5")
            rows = cursor.fetchall()
            for row in rows:
                result.append(row)
        cnx.close()
    else:
        result = "Could not connect to DB"

    try:
        question = urllib.request.urlopen("http://internal-polls-1382146748.ap-southeast-1.elb.amazonaws.com:8000").read()
    except Exception as err:
        app.logger.error("Could not connect to Polls: %s", err)
        question = "Could not connect to Polls: {}".format(err)

    return render_template('index.html', result=result, question=question)


@app.route('/create-service-table')
def create_service():
    result = []
    try:
        cnx = mysql.connector.connect(**config)
    except Exception as err:
        app.logger.error("Could not connect to DB: %s", err)
        result = "Could not connect to DB"
        return render_template('index.html', result=result)

    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            cursor.execute("CREATE TABLE service (name VARCHAR(255), endpoint VARCHAR(255))")
        cnx.close()
    else:
        result = "Could not connect to DB"

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
