from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY']='EstoEsUnSecreto'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/tasks.db'

login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

db = SQLAlchemy(app)

admin = Admin(app)

class MyModelView(ModelView):
    def is_accessible(self):
        if(current_user.is_authenticated):
        	return current_user.user_name=="danieldiaz"
        return False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('index', next=request.url))

class LoginForm(FlaskForm):
	user_name = StringField('username', validators=[InputRequired(), Length(min=4,max=15)])
	password= PasswordField('password', validators=[InputRequired(), Length(min=8,max=80)])
	remember= BooleanField('remember me') 

class RegisterForm(FlaskForm):
	user_name = StringField('username', validators=[InputRequired(), Length(min=4,max=15)])
	email= StringField('email', validators=[InputRequired(), Email(message='Invalid Email'),Length(max=50)])
	password= PasswordField('password', validators=[InputRequired(), Length(min=8,max=80)])
	

class User(UserMixin, db.Model):
	id=db.Column(db.Integer, primary_key=True)
	user_name=db.Column(db.String(15),unique=True)
	email=db.Column(db.String(50),unique=True)
	password = db.Column(db.String(80))

admin.add_view(MyModelView(User,db.session))

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class Task(db.Model):

	id=db.Column(db.Integer, primary_key=True)
	content=db.Column(db.String(200))
	done=db.Column(db.Boolean)

admin.add_view(MyModelView(Task,db.session))
		


@app.route("/",methods=['GET','POST'])
def index():
	form = LoginForm()
	if form.validate_on_submit():
		user=User.query.filter_by(user_name=form.user_name.data).first()
		if user:
			if check_password_hash(user.password, form.password.data):
				login_user(user, remember=form.remember.data)
				return redirect(url_for('task'))
		return 'Invalid username or password'
	return render_template('index.html',form=form)

@app.route("/SignUp",methods=['GET','POST'])
def sign_up():
	form=RegisterForm()
	if form.validate_on_submit():
		hashed_password = generate_password_hash(form.password.data, method='sha256')
		new_user=User(user_name=form.user_name.data, email=form.email.data, password=hashed_password)
		db.session.add(new_user)
		db.session.commit()
		return "User created"
	return render_template('sign_up.html',form=form)

@app.route("/task")
@login_required
def task():
	tasks=Task.query.all()
	return render_template('task.html', list=tasks)


@app.route("/create-task",methods=['POST'])
@login_required
def create():
    task=Task(content=request.form['content'], done=False)
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('task'))

@app.route("/save-task/<id>",methods=['POST'])
@login_required
def save(id):
	task=Task.query.filter_by(id=int(id)).first()
	task.content=request.form['content']
	db.session.commit()
	return redirect(url_for('task'))

@app.route('/done/<id>')
@login_required
def done(id):
	task=Task.query.filter_by(id=int(id)).first()
	task.done=not(task.done)
	db.session.commit()
	return redirect(url_for('task'))


@app.route("/edit/<id>")
@login_required
def edit(id):
	task=Task.query.filter_by(id=int(id)).first()
	return render_template('edit.html', task=task)

@app.route("/delete/<id>")
@login_required
def delete(id):
	#task=Task.query.filter_by(id=int(id)).first()
	task=Task.query.filter_by(id=int(id)).delete()
	db.session.commit()
	return redirect(url_for('task'))

@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
