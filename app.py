from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, validates
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.helpers import is_form_submitted
from flask_admin.model.base import BaseModelView


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

	#def validate_form(self, form):
	#	""" My model admin model view """		
	#	if is_form_submitted():
	#		if isinstance(form, self.delete_form()):
	#			return super(MyModelView, self).validate_form(form)
	#		if (form.fecha_plazo_final.data<form.fecha_inicio.data):
	#			flash("La fecha de inicio no puede ser superior a la de fin")
	#			return False
	#		return super(MyModelView, self).validate_form(form)
	#	return super(MyModelView, self).validate_form(form)
  

class Task(db.Model):
	__tablename__='Task'
	id=db.Column(db.Integer, primary_key=True)
	nombre=db.Column(db.String(50),nullable=False)
	descripcion=db.Column(db.String(200), nullable=False)
	fecha_inicio=db.Column(db.Date, nullable=False)
	fecha_fin=db.Column(db.Date)
	estado=db.Column(db.Boolean)
	id_proceso = db.Column(db.Integer, db.ForeignKey('Proceso.id'))
	proceso = relationship("Proceso",backref="Tasks")

	def __repr__(self):
		return '<Paso %r>' % (self.nombre)

class User(UserMixin, db.Model):
	__tablename__='User'
	id=db.Column(db.Integer, primary_key=True)
	user_name=db.Column(db.String(15),unique=True)
	email=db.Column(db.String(50),unique=True)
	num_cel=db.Column(db.Integer)
	cedula=db.Column(db.Integer)
	password = db.Column(db.String(80))
	especialidad = db.Column(db.String(50))
	def __repr__(self):
		return '<User %r>' % (self.user_name)        

class Categoria(db.Model):
	__tablename__='Categoria'
	id=db.Column(db.Integer, primary_key=True)
	nombre=db.Column(db.String(50),nullable=False)
	descripcion=db.Column(db.String(200), nullable=False)
	def __repr__(self):
		return '<Categoria %r>' % (self.nombre)


class Proceso(db.Model):
	__tablename__='Proceso'
	id=db.Column(db.Integer, primary_key=True)
	nombre=db.Column(db.String(50),nullable=False)
	descripcion=db.Column(db.String(200), nullable=False)
	fecha_entrega=db.Column(db.Date, nullable=False)

	id_categoria = db.Column(db.Integer, db.ForeignKey('Categoria.id'))
	categoria = relationship("Categoria",backref="Procesos")
	user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
	user = relationship("User",backref="Procesos")

	def __repr__(self):
		return '<Proceso %r>' % (self.nombre)

class LoginForm(FlaskForm):
	user_name = StringField('username', validators=[InputRequired(), Length(min=4,max=15)])
	password= PasswordField('password', validators=[InputRequired(), Length(min=8,max=80)])
	remember= BooleanField('remember me') 

class RegisterForm(FlaskForm):
	user_name = StringField('username', validators=[InputRequired(), Length(min=4,max=15)])
	email= StringField('email', validators=[InputRequired(), Email(message='Invalid Email'),Length(max=50)])
	password= PasswordField('password', validators=[InputRequired(), Length(min=8,max=80)])
	
admin.add_view(MyModelView(User,db.session))

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))



admin.add_view(MyModelView(Task,db.session))
admin.add_view(MyModelView(Proceso,db.session))
admin.add_view(MyModelView(Categoria,db.session))

		


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
	tasks=Proceso.query.filter_by(user_id=current_user.id) #corregir tasks por procesos
	return render_template('task.html', list=tasks)


""" @app.route("/create-task",methods=['POST'])
@login_required
def create():
    task=Task(content=request.form['content'], done=False)
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('task')) """

""" @app.route("/save-task/<id>",methods=['POST'])
@login_required
def save(id):
	task=Task.query.filter_by(id=int(id)).first()
	task.content=request.form['content']
	db.session.commit()
	return redirect(url_for('task')) """

@app.route('/done/<id>')
@login_required
def done(id):
	task=Task.query.filter_by(id=int(id)).first()
	task.estado=not(task.estado)
	db.session.commit()
	return redirect(url_for('task'))


""" @app.route("/edit/<id>")
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
 """
@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
