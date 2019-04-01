import time
import threading
import datetime as dt
import os
from collections import namedtuple

import pandas as pd
import pigpio

RED = 22
BLUE = 17
GREEN = 6 

SAVED_COLORS = 'saved_colors.csv'

class Stopper:
	def __init__(self):
		self.stop=False
		self.current=None
		self.saved_colors=None
		self.saved_color_buttons=None

Color = namedtuple('Color', ['r', 'g', 'b'])

def semaphorize(sem, logger=None):
	def f_wrap(func):
		def a_wrap(*args, **kwargs):
			if logger:
				logger(f'semaphore acquiring {func.__name__}')
			sem.acquire()
			if logger:
				logger(f'semaphore acquired {func.__name__}')
			func(*args, **kwargs)
			sem.release()
			if logger:
				logger(f'semaphore released {func.__name__}')
		return a_wrap
	return f_wrap


def hex_to_rgb(hex):
	h = hex.lstrip('#')
	return tuple(int(h[i:i+2], 16) for i in (0, 2 ,4))

def rgb_to_hex(rgb, hash=False):
	prefix = '#' if hash else ''
	return prefix + f'{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'


def interpolate(l, r, t0, dt, t):
	"""
	this is a poorly written function that linearly interpolates
	l and r based on the position of t between tl and tr
	"""
	p = (t-t0)/dt
	return [p*(j-i) + i for i, j in zip(l, r)]

def show(color):
	pi = pigpio.pi()
	# print(f"{color[0]:.2}\t{color[1]:.2}\t{color[2]:.2}")
	pi.set_PWM_dutycycle(RED, color[0])
	pi.set_PWM_dutycycle(GREEN, color[1])
	pi.set_PWM_dutycycle(BLUE, color[2])
	pi.stop()

def now():
	return dt.datetime.now()

def  flash(colors, delay, exit=None):
	"""
	flashes a list of colors for time on and time off
	"""
	seconds = delay
	if isinstance(time, dt.timedelta):
		seconds = time.total_seconds()
	i = 0
	l = len(colors)
	while True:
		show(colors[i])
		time.sleep(seconds)
		show((0,0,0))

		if exit.stop:
			break

		time.sleep(seconds)
		i = (i+1) % l


def fade(colors, lengths, exit=None, sem=None, steps=500, action=show):
	"""
	fades between colors with specified lengths 
	inputs:
		colors: list of 3-tuples
		lengths: list of lengths (in timedeltas?) between n and n+1 color
			will repeat if len(colors) == len(lengths)
		exit: somehow an exit condition
		repeat: start from the beginning if all colors shown
	"""
	sem.acquire()
	if (not colors) or (not lengths):
		return

	n = len(lengths)
	c = len(colors)
	repeat = (len(colors) == n)

	total = sum(lengths, dt.timedelta())
	pause = (total/steps).total_seconds()

	last = now()
	i = 0
	while True:
		t = now()
		if t - last > lengths[i]:
			i += 1
			if i >= n:
				if repeat:
					i %= n
				else:
					break
			last = last + lengths[i]
		color = interpolate(colors[i], colors[(i+1) % c], last, lengths[i], t)
		action(color)
		if exit.stop:
			sem.release()
			return
		time.sleep(pause)

def sunrise(length=dt.timedelta(seconds=30), exit=None, sem=None, steps=500, action=show):
	colors = [(0,0,0), (255,0,0), (255,180,0), (255,255,255)]
	lengths = [length/len(colors)]*(len(colors)-1)

	fade(colors, lengths, exit=exit, sem=sem, steps=steps, action=action)


def rainbow(length=dt.timedelta(seconds=9), exit=None, sem=None, steps=300, action=show):
	colors = [(255,0,0), (255,128,0), (0,255,0), (0,255, 200), (0,0,255), (255, 0, 255)]
	lengths = [length/len(colors)]*(len(colors))

	fade(colors, lengths, exit=exit, sem=sem, steps=steps, action=action)


def save_colors(color, saved_colors, path):
	"""
	saves a color to the saved colors csv
	color: (r, g, b)
	"""
	if color != None:
		named_color = Color(*color)
		saved_colors.loc[rgb_to_hex(color)] = named_color
	saved_colors.drop_duplicates().to_csv(path, index=False)
	return saved_colors

def load_colors(path):
	"""
	loads saved colors from csv
	returns pandas df of saved colors
	"""
	# if os.path.exists(path):
	try:
		saved_colors = pd.read_csv(path, header=0)
	except:
		saved_colors = pd.DataFrame(columns=['r', 'g', 'b'])
		saved_colors.to_csv(path, index=False)
	return saved_colors

def make_saved_color_buttons(saved_colors):
	"""
	makes html to load saved colors
	"""
	form_string = ['<form action="/saved_color.html" method="post">']
	for color in saved_colors[['r', 'g', 'b']].values:
		hex_color = rgb_to_hex(color)
		form_string.append(f'\t<input type="submit" style="backgroundcolor:{hex_color}" value={hex_color} name="color">')
	form_string.append('</form>')
	return '\n'.join(form_string)


def main():
	alarm_flag = True
	start = dt.datetime(2019, 1, 11, 6, 25, 0)
	while alarm_flag:
		print('.')
		if now() > start:
			alarm_flag = False
			t = threading.Thread(target=sunrise, kwargs={'length':dt.timedelta(minutes=30)})
			t.start()
		time.sleep(60)


if __name__ == '__main__':
	main()
