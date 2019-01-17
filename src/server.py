from flask import Flask, request, render_template
from light_utils import *

app = Flask(__name__)
app.run(host='0.0.0.0', port=5050, debug=True)

stopper = Stopper()

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/color.html', methods=['POST', 'GET'])
def change_color():
	error = None
	if request.method == 'POST':
		stopper.stop = True
		color = request.form['color']
		color = hex_to_rgb(color)
		show(color)
		stopper.stop = False
		print(request.method)
	else:
		color = 'bad boy!'
	return render_template('index.html', current=color)

@app.route('/rainbow.html', methods=['POST', 'GET'])
def make_rainbow():
	stopper.stop = True
	time.sleep(0.001)
	if request.method == 'POST':
		stopper.stop = False
		rainbow(exit=stopper)
	return render_template('index.html', current='Rainbow!!!')