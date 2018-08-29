# coding=utf-8
from flask import Flask


app = Flask(__name__)
app.config.from_object('config')


@app.route('/geet/<name>')
def hello(name):
    return '<h1>Hello %s!</h1>' % name


@app.route('/num/<num>/')
def show_num(num):
    return 'The number is {}'.format(num)
