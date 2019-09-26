from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello World!"
@app.route("/hola/<int:num>")
def hola(num):
    return "Hola {}".format(num)
if __name__ == "__main__":
    app.run(debug=True)