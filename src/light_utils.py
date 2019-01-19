import time
import threading
import datetime as dt
import pigpio

RED = 22
BLUE = 17
GREEN = 6 

class Stopper:
	def __init__(self):
		self.stop=False

def hex_to_rgb(hex):
	h = hex.lstrip('#')
	return tuple(int(h[i:i+2], 16) for i in (0, 2 ,4))

def rgb_to_hex(rgb):
	return None


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
