import time
import threading
import datetime as dt
import pigpio

RED = 22
BLUE = 17
GREEN = 6 

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
		show(color)
		time.sleep(seconds)
		show((0,0,0))

		if exit:
			break

		time.sleep(seconds)


def fade(colors, lengths, exit=None, steps=500, action=show):
	"""
	fades between colors with specified lengths 
	inputs:
		colors: list of 3-tuples
		lengths: list of lengths (in timedeltas?) between n and n+1 color
			will repeat if len(colors) == len(lengths)
		exit: somehow an exit condition
		repeat: start from the beginning if all colors shown
	"""
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
		if exit:
			break
		time.sleep(pause)

def sunrise(length=dt.timedelta(seconds=30), exit=None, steps=500, action=show):
	colors = [(0,0,0), (255,0,0), (255,180,0), (255,255,255)]
	lengths = [length/len(colors)]*(len(colors)-1)

	fade(colors, lengths, exit=exit, steps=steps, action=action)


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
