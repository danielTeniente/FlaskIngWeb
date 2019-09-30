from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/tasks.db'
db = SQLAlchemy(app)

class Task(db.Model):
	"""docstring for Task"""
	id=db.Column(db.Integer, primary_key=True)
	content=db.Column(db.String(200))
	done=db.Column(db.Boolean)
		


@app.route("/")
def index():
	tasks=Task.query.all()
	return render_template('index.html', list=tasks)


@app.route("/create-task",methods=['POST'])
def create():
    task=Task(content=request.form['content'], done=False)
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route("/save-task/<id>",methods=['POST'])
def save(id):
	task=Task.query.filter_by(id=int(id)).first()
	task.content=request.form['content']
	db.session.commit()
	return redirect(url_for('index'))

@app.route('/done/<id>')
def done(id):
	task=Task.query.filter_by(id=int(id)).first()
	task.done=not(task.done)
	db.session.commit()
	return redirect(url_for('index'))


@app.route("/edit/<id>")
def edit(id):
	task=Task.query.filter_by(id=int(id)).first()
	return render_template('edit.html', task=task)

@app.route("/delete/<id>")
def delete(id):
	#task=Task.query.filter_by(id=int(id)).first()
	task=Task.query.filter_by(id=int(id)).delete()
	db.session.commit()
	return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)