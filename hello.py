from datetime import datetime
from flask import Flask, request, flash, url_for, redirect, \
     render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_pyfile('hello.cfg')
db = SQLAlchemy(app)


class Todo(db.Model):
    __tablename__ = 'test'
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(60))

    def __init__(self, title, text):
        self.id = id
        self.name = text


@app.route('/')
def show_all():
    return render_template('show_all.html',
        todos=Todo.query.order_by(Todo.id.desc()).all()
    )


@app.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        if not request.form['id']:
            flash('id is required', 'error')
        elif not request.form['name']:
            flash('name is required', 'error')
        else:
            todo = Todo(request.form['id'], request.form['name'])
            db.session.add(todo)
            db.session.commit()
            flash(u'profil item was successfully created')
            return redirect(url_for('show_all'))
    return render_template('new.html')


@app.route('/update', methods=['POST'])
def update_done():
    for todo in Todo.query.all():
        todo.done = ('done.%d' % todo.id) in request.form
    flash('Updated status')
    db.session.commit()
    return redirect(url_for('show_all'))


if __name__ == '__main__':
    app.run()
