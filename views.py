from app import app

@app.route("/Consultas",methods=['GET','POST'])
def consultas():
	return "Consulta"
