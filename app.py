from flask import Flask, render_template
import mysql.connector
import logging

app = Flask(__name__)

config = {
  'user': 'abyan',
  'password': '7kxtaHVie4MEpufAp7LU',
  'host': 'terraform-20240422044038018300000001.c4avp797njw5.ap-southeast-1.rds.amazonaws.com',
  'database': 'superservice',
  'port': '3306',
  'raise_on_warnings': True
}

@app.route('/healthcheck')
def healthcheck():
    try:
        cnx = mysql.connector.connect(**config)
    except mysql.connector.Error as err:
        app.logger.error("Could not connect to DB: %s", err)
        return "Could not connect to DB"
    if cnx.is_connected():
        return "OK"
    cnx.close()


@app.route('/')
def index():
    result = []
    return render_template('index.html', result=result)


@app.route('/polls')
def polls():
    return render_template('polls.html')


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
    gunicorn_logger = logging.getLogger('gunicorn.warn')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
