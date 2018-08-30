# coding=utf-8
from flask import Flask, redirect, url_for, abort, make_response, json, jsonify, request, session
import click
import os

app = Flask(__name__)
# app.config.from_object('config')
app.secret_key = os.getenv('SECRET_KEY', 'default simple secret key')


@app.route('/')
def homepage():
    return '<h1>Flask rule the world!</h1>'


@app.route('/geet/<name>/')
def name(name):
    return '<h1>Hello %s!</h1>' % name


@app.route('/num/<int:num>/')
def show_num(num):
    return 'The number is {}'.format(num)


@app.cli.command()
def helloworld():
    """Say hello"""
    click.echo("Hello World!")


@app.route('/goback/<int:year>/')
def goback(year):
    return "<h1>It was {0} {1} years ago!</h1>".format(2018-year, year)


@app.route('/colors/<any(blue,red,black):color>/')
def color(color):
    return "<h1>It is right color!</h1>"


@app.route('/change/')
def change():
    return '', 302, {'Location': 'http://news.sina.com.cn'}


@app.route('/4004/')
def go_nowhere():
    abort(404)


@app.route('/text/')
def plain_text():
    response = make_response('Just a few texts as plain text doc.')
    response.mimetype = 'text/plain'
    return response


@app.route('/json/')
def use_json():
    data = {
        'name': 'Reed',
        'age': 34,
        'gender': 'male'
    }
    response = make_response(json.dumps(data))
    response.mimetype = 'application/json'
    return response


@app.route('/jsonify/')
def use_jsonify():
    data = {
        'name': 'Reed',
        'age': 34,
        'gender': 'male'
    }
    # response = make_response(json.dumps(data))
    # response.mimetype = 'application/json'
    return jsonify(data)


@app.route('/hello/')
def say_hello():
    name = request.cookies.get('name')
    if name is not None:
        return '<h1>Flask rule the world!</h1><p>Hello {}</p>'.format(name)
    else:
        return '<h1>No cookie found!</h1>'


@app.route('/set/<string:name>')
def set_cookie(name):
    response = make_response(redirect(url_for('say_hello')))
    response.set_cookie('name', name)
    return response


@app.route('/hi/')
def hi():
    response = '<h1>Flask help the world!</h1>'
    if 'logged_in' in session:
        response += '<p>You are logged in now.</p>'
    else:
        response += '<p>You are NOT logged in.</p>'
    return response


@app.route('/login/')
def do_login():
    session['logged_in'] = True
    return redirect(url_for('hi'))


@app.route('/logout/')
def do_logout():
    if 'logged_in' in session:
        session.pop('logged_in')
    return redirect(url_for('hi'))
