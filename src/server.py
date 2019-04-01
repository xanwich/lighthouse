from flask import Flask, request, render_template

from light_utils import *

app = Flask(__name__)

stopper = Stopper()
sem = threading.BoundedSemaphore(value=1)
stopper.saved_colors = load_colors(SAVED_COLORS)
stopper.saved_color_buttons = make_saved_color_buttons(stopper.saved_colors)

def _index():
	hex_colors = [(rgb_to_hex(color), f'background-color:{rgb_to_hex(color, hash=True)}') for color in stopper.saved_colors[['r', 'g', 'b']].values]
	return render_template('index.html', hex_colors=hex_colors)

@app.route('/')
def index():
	return _index()

@app.route('/color.html', methods=['POST', 'GET'])
def change_color():
	error = None
	if request.method == 'POST':
		# tell any current running threads to stop
		stopper.stop = True
		# get color
		form = request.get_json(force=True)
		app.logger.debug(form)
		color = form['color']
		color = hex_to_rgb(color)
		# wait until threads have actually stopped
		sem.acquire()
		show(color)
		stopper.current=color
		app.logger.debug(color)
		stopper.stop = False
		sem.release()
	else:
		color = 'bad boy!'
	return _index()

@app.route('/rainbow.html', methods=['POST', 'GET'])
def make_rainbow():
	stopper.stop = True
	time.sleep(0.001)
	if request.method == 'POST':
		stopper.stop = False
		rainbow(exit=stopper, sem=sem)
		stopper.current='rainbow'
		current = 'rainbow'
	return _index()

@app.route('/off.html', methods=['POST', 'GET'])
def off():
	stopper.stop = True
	sem.acquire()
	show((0, 0, 0))
	current = (0, 0, 0)
	stopper.stop = False
	sem.release()
	return _index()

@app.route('/save.html', methods=['POST', 'GET'])
def save():
	if request.form['command'] == 'save':
		if stopper.current != 'rainbow':
			stopper.saved_colors = save_colors(stopper.current, stopper.saved_colors, SAVED_COLORS)
			stopper.saved_color_buttons = make_saved_color_buttons(stopper.saved_colors)
	elif request.form['command'] == 'delete':
		saved_colors = stopper.saved_colors
		saved_colors = saved_colors[
			(saved_colors['r'] != stopper.current[0]) &
			(saved_colors['g'] != stopper.current[1]) &
			(saved_colors['b'] != stopper.current[2])
		]
		stopper.saved_colors = saved_colors
		if stopper.current != 'rainbow':
			stopper.saved_colors = save_colors(stopper.current, stopper.saved_colors, SAVED_COLORS)
	return _index()

@app.route('/saved_color.html', methods=['POST', 'GET'])
def saved_color():
	app.logger.debug(dir(request))
	if request.method == 'POST':
		color = request.form['color']
		color = hex_to_rgb(color)
		stopper.stop = True
		sem.acquire()
		show(color)
		stopper.current = color
		stopper.stop = False
		sem.release()
	return _index()


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)
