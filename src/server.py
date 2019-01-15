from flask import Flask, request, render_template
from light_utils import *

app = Flask(__name__)
app.run(host='0.0.0.0', port=5050)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/color.html', methods=['POST', 'GET'])
def change_color():
	error = None
	if request.method == 'POST':
		color = request.form['color']
		color = hex_to_rgb(color)
		show(color)
		print(request.method)
	else:
		color = 'bad boy!'
	return render_template('color.html', current=color)
