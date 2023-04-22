from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    param = {}
    param['title'] = 'колонизация'
    return render_template('index.html', **param)

@app.route('/training/<prof>')
def training(prof):
    param = {}
    param['speciality'] = prof
    print(param['speciality'])
    param['title'] = param['speciality']
    return render_template('training.html', **param)

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')