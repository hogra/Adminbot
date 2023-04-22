from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/index')
def index():
    param = {}
    param['title'] = 'ТОВАРИЩ АДМИН'
    return render_template('index.html', **param)

app.run(port=8080, host='127.0.0.1')