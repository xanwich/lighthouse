import time
import threading
import datetime as dt

def interpolate(l, r, t0, dt, t):
	"""
	this is a poorly written function that linearly interpolates
	l and r based on the position of t between tl and tr
	"""
	p = (t-t0)/dt
	return (p*(j-i) + i for i, j in zip(l, r))

def show(color):
	print(*color)

def now():
	return dt.datetime.now()

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
		color = interpolate(colors[i], colors[(i+1) % n], last, lengths[i], t)
		action(color)
		if exit:
			break
		time.sleep(pause)

def sunrise(length=dt.timedelta(seconds=30), exit=None, steps=500, action=show):
	colors = [(0,0,0), (255,0,0), (255,225,0), (255,255,255)]
	lengths = [length/len(colors)]*(len(colors))

	fade(colors, lengths, exit=exit, steps=steps, action=action)

if __name__ == '__main__':
	sunrise()
