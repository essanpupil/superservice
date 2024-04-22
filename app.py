from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

config = {
  'user': 'abyan',
  'password': 'password',
  'host': 'terraform-20240422044038018300000001.c4avp797njw5.ap-southeast-1.rds.amazonaws.com',
  'database': 'superservice',
  'raise_on_warnings': True
}

@app.route('/healthcheck')
def healthcheck():
    cnx = mysql.connector.connect(**config)
    if cnx.is_connected():
        return "OK"
    cnx.close()


@app.route('/')
def index():
    result = []
    cnx = mysql.connector.connect(**config)
    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            cursor.execute("SELECT * FROM service LIMIT 5")
            rows = cursor.fetchall()
            for row in rows:
                result.append(row)
        cnx.close()
    else:
        result = "Could not connect to DB"
    return render_template('index.html', result=result)


@app.route('/polls')
def polls():
    return render_template('polls.html')


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
