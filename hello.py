from datetime import datetime, date, time
import decimal
import uuid
import json

from flask import Flask, request, flash, url_for, redirect, \
     render_template, jsonify
from flask_sqlalchemy import SQLAlchemy


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime):
            return o.isoformat(sep=' ', timespec='seconds')
        if isinstance(o, date):
            return o.isoformat()
        if isinstance(o, time):
            return o.isoformat(timespec='seconds')
        if isinstance(o, (decimal.Decimal, uuid.UUID)):
            return str(o)
        else:
            return super().default(o)


app = Flask(__name__)
# app.json_encoder = CustomJSONEncoder
app.config.from_pyfile('hello.cfg')
db = SQLAlchemy(app)


class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    text = db.Column(db.String(191))
    done = db.Column(db.Boolean)
    pub_date = db.Column(db.DateTime)
    update_date = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)

    def __init__(self, title, text):
        self.title = title
        self.text = text
        self.done = False
        self.pub_date = datetime.utcnow()

    def to_dict(self):
        keys = [x.name for x in self.__table__.columns]
        return {x: getattr(self, x) for x in keys}


@app.route('/create_all')
def create_all():
    r = db.create_all()
    print(r)
    return 'create all'


@app.route('/')
def show_all():
    return render_template('show_all.html', todos=Todo.query.order_by(Todo.pub_date.desc()).all())


@app.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        if not request.form['title']:
            flash('Title is required', 'error')
        elif not request.form['text']:
            flash('Text is required', 'error')
        else:
            todo = Todo(request.form['title'], request.form['text'])
            db.session.add(todo)
            db.session.commit()
            flash(u'Todo item was successfully created')
            return redirect(url_for('show_all'))
    return render_template('new.html')


@app.route('/update', methods=['POST'])
def update_done():
    for todo in Todo.query.all():
        todo.done = ('done.%d' % todo.id) in request.form
    flash('Updated status')
    db.session.commit()
    return redirect(url_for('show_all'))


@app.route('/todos/<int:todo_id>')
def item(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    return jsonify(todo.to_dict())


if __name__ == '__main__':
    app.run(host='0.0.0.0')
