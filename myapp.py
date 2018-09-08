# -*- coding: utf-8 -*-

import os

import click
from flask import (Flask, abort, flash, json, jsonify, make_response, redirect,
                   render_template, request, session, url_for)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from jinja2 import escape
from jinja2.utils import generate_lorem_ipsum
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired

try:
    from urlparse import urlparse, urljoin  # for py3
except ImportError:
    from urllib.parse import urlparse, urljoin  # for py2


app = Flask(__name__)
# app.config.from_object('config')
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.secret_key = os.getenv('SECRET_KEY', 'default simple secret key')
app.config['SQLALCHEMY_DATABASE_URI'] = \
    os.getenv('DATABASE_URL', 'sqlite:///' +
              os.path.join(app.root_path, 'data.sqlite'))

# Flask-SQLAlchemy建议你设置SQLALCHEMY_TRACK_MODIFICATIONS配置变量,
# 这个配置变量决定是否追踪对象的修改,这用于Flask-SQLAlchemy的事件通知系统.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


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


@app.route('/login/')
def do_login():
    session['logged_in'] = True
    return redirect(url_for('hi'))


@app.route('/logout/')
def do_logout():
    if 'logged_in' in session:
        session.pop('logged_in')
    return redirect(url_for('hi'))


def redirect_back(default='hi', **kwargs):
    print('next is: ' + request.args.get('next'))
    print('request.referrer is: ' + request.referrer)
    for target in request.args.get('next'), request.referrer:
        # if target:
        #     if is_safe_url(target):
        #         return redirect(target)
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


@app.route('/working_on_login/')
def make_login():
    print('\n')
    print('         make_login() is called!')
    print(request.full_path)
    print('\n')
    return redirect_back()


@app.route('/do_big_thing/')
def do_big_thing():
    return '<h1>do big things</h1><a href="%s">click \
        here to make login</a>' % url_for('make_login', next=request.full_path)


@app.route('/do_bad_thing/')
def do_bad_thing():
    return '<h1>do big things</h1><a href="%s">click \
        here to make login</a>' % url_for('make_login', next='http://www.baidu.com/')


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    print('\n')
    print('target is: ' + target)
    print(ref_url)
    print(test_url)
    print('\n')
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


# AJAX sample
@app.route('/post')
def show_post():
    post_body = generate_lorem_ipsum(n=2)
    return '''
<h1>A very long post</h1>
<div class="body">%s</div>
<button id="load">Load More</button>
<script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
<script type="text/javascript">
$(function() {
    $('#load').click(function() {
        $.ajax({
            url: '/more',
            type: 'get',
            success: function(data){
                $('.body').append(data);
            }
        })
    })
})
</script>''' % post_body


@app.route('/more')
def load_post():
    return generate_lorem_ipsum(n=1)


# Run 'flask' and see it's in Commands list
@app.cli.command()
def initdb():
    """
    Init the database
    """
    db.drop_all()
    db.create_all()
    click.echo('Initialized database')


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)

    def __repr__(self):
        return 'Note [%d] %r' % (self.id, self.body)


class NewNoteForm(FlaskForm):
    body = TextAreaField('Body', validators=[DataRequired()])
    submit = SubmitField('Save')


class DeleteNoteForm(FlaskForm):
    submit = SubmitField('Delete')


class EditNoteForm(FlaskForm):
    body = TextAreaField('Body', validators=[DataRequired()])
    submit = SubmitField('Update')

    # def __init__(self, lable="Update", **kwargs):
    #     super().__init__()
    #     self.submit.lable = wtforms.Lable(self.submit.id, lable)


@app.route('/new/', methods=['GET', 'POST'])
def new_note():
    form = NewNoteForm()
    if form.validate_on_submit():
        body = form.body.data
        note = Note(body=body)
        db.session.add(note)
        db.session.commit()
        flash('Your note is saved.')
        return redirect(url_for('hi'))
    return render_template('new_note.html', form=form)


@app.route('/edit/<int:note_id>/', methods=['GET', 'POST'])
def edit_note(note_id):
    form = EditNoteForm()
    note = Note.query.get(note_id)
    if form.validate_on_submit():
        note.body = form.body.data
        db.session.commit()
        flash('The note is updated.')
        return redirect(url_for('hi'))
    form.body.data = note.body
    return render_template('edit_note.html', form=form)


@app.route('/delete/<int:note_id>/', methods=['GET', 'POST'])
def delete_note(note_id):
    form = DeleteNoteForm()
    if form.validate_on_submit():
        note = Note.query.get(note_id)
        db.session.delete(note)
        db.session.commit()
        flash('The note is deleted.')
    else:
        about(400)
    return redirect(url_for('hi'))


@app.route('/hi/')
def hi():
    # response = '<h1>Flask help the world!</h1>'
    # if 'logged_in' in session:
    #     response += '<p>You are logged in now.</p>'
    # else:
    #     response += '<p>You are NOT logged in.</p>'
    # print('------------------------------')
    # print(request.full_path)
    # print('------------------------------')
    # return response

    delete_note_form = DeleteNoteForm()
    edit_note_form = EditNoteForm()
    notes = Note.query.all()
    return render_template('hi.html', \
            notes=notes, delete_form=delete_note_form, edit_form=edit_note_form)


@app.shell_context_processor # 标记为flash shell后会自动执行
def generate_shell_context():
    return dict(db=db, Note=Note, Author=Author, \
            Article=Article, initdb=initdb, Book=Book, \
            Writer=Writer, Country=Country, Capital=Capital)


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=True)
    phone = db.Column(db.String(20))
    article = db.relationship('Article', uselist=False)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), index=True)
    body = db.Column(db.Text)

    # Flask-SQLlchemy自动生成的表名，是对应Model类的类名的小写形式，多个单词则用
    # 下划线连接，表名也可以显性的在Model类里定义__tablename__熟悉，
    # 所以这里定义db.ForeignKey，使用 author.id 参数，即表示指向 author 表的 id 字段
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))


class Writer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=True)
    books = db.relationship('Book', back_populates='writer')


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), index=True)
    writer_id = db.Column(db.Integer, db.ForeignKey('writer.id'))
    writer = db.relationship('Writer', back_populates='books')


class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=True)
    capital = db.relationship('Capital', uselist=False)

    def __repr__(self):
        return '<Country %r>' % self.name


class Capital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'))
    country = db.relationship('Country', uselist=False)

    def __repr__(self):
        return '<Capital %r>' % self.name

