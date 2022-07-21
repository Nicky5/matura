import pygame
import time
import math
import random
from math import sqrt
from pygame.mouse import get_pos
from collections import namedtuple
from shapely.geometry import Polygon

tiles = namedtuple('tiles', ['n', 'ne', 'se', 's', 'sw', 'nw'])
Point = namedtuple('Point', ['x', 'y'])

size = 32
ringnum = 5
hexes = []

frame = 1792, 896

pygame.display.set_caption('killer')

start_time = time.time() - 0.5

drag = False
startpoint = 0, 0
lastoffset = 1792/2, 896/2

offset = 1792/2, 896/2
scale = 1

mouse = False
class Hexagon:

	def __init__(self):
		self.index = -2
		self.q = 0
		self.r = 0
		self.points: any
		self.center: any
		self.size: any
		self.triangleheight: any

		self.tiles = [None, None, None, None, None, None]

	@staticmethod
	def from_size_and_center(i, l, x, y):
		"""
		Create a hexagon centered on (x, y)
		:param l: length of the hexagon's edge
		:param x: x-coordinate of the hexagon's center
		:param y: y-coordinate of the hexagon's center
		:return: The polygon containing the hexagon's coordinates
		"""
		poly = Hexagon()
		poly.index = i
		poly.points = [Point(round(x + math.cos(math.radians(angle)) * l, 3), round(y + math.sin(math.radians(angle)) * l, 3)) for angle in range(0, 360, 60)]
		poly.center = Point(round(x, 3), round(y, 3))
		poly.size = l
		poly.triangleheight = math.sqrt(l**2 - (l/2)**2)
		return poly

	def from_axial_point(q, r, size):
		poly = Hexagon()
		poly.center = Point(round(size * (3./2 * q), 3), round(size * (sqrt(3)/2 * q + sqrt(3) * r), 3))
		poly.points = [Point(round(poly.center.x + math.cos(math.radians(angle)) * size, 3), round(poly.center.y + math.sin(math.radians(angle)) * size, 3)) for angle in range(0, 360, 60)]
		poly.size = size
		poly.triangleheight = math.sqrt(size**2 - (size/2)**2)
		return poly

	def render(self, screen, color=(255, 255, 255), width=0):
		points = [((i.x*scale) + offset[0], (i.y*scale) + offset[1]) for i in self.points]
		pygame.draw.polygon(screen, color, points)
		pygame.draw.polygon(screen, (0, 0, 0), points, width)
		

	# def get_ring(self):
	# 	i = 0
	# 	while ((i ** 2 + i)//2) * 6 < a+1:
	# 		i += 1
	# 	return i

	def flat_hex_to_pixel(self):
		x = self * (3./2 * self.q)
		y = self * (sqrt(3)/2 * self.q  +  sqrt(3) * self.r)
		return Point(x, y)
def tuple_add(tuple1, tuple2):
	return tuple1[0] + tuple2[0], tuple1[1] + tuple2[1]

def tuple_subtract(tuple1, tuple2):
	return tuple1[0] - tuple2[0], tuple1[1] - tuple2[1]

def tuple_factor(tuple1, factor):
	return tuple1[0] * factor, tuple1[1] * factor

def point_are_close(a, b):
	return (math.isclose(a.x, b.x) and math.isclose(a.y, b.y))

def generate_hexes(ringnum, size):
	global hexes

	for r in range(-ringnum, ringnum+1):
		qdinates = []
		if r < 0:
			for q in range(-(r+ringnum), 0):
				qdinates.append(Hexagon.from_axial_point(q, r, size))
			for q in range(ringnum+1):
				qdinates.append(Hexagon.from_axial_point(q, r, size))
		elif r == 0:
			for q in range(-ringnum, ringnum+1):
				qdinates.append(Hexagon.from_axial_point(q, r, size))
		elif r > 0:
			for q in range(-ringnum, 0):
				qdinates.append(Hexagon.from_axial_point(q, r, size))
			for q in range(ringnum-r+1):
				qdinates.append(Hexagon.from_axial_point(q, r, size))
		hexes.append(qdinates)



	# center = Hexagon.from_size_and_center(-1, size, 0, 0)
	# for ring in range(ringnum):
	# 	points = [Point(center.center.x + math.sin(math.radians(angle)) * (center.size * 2), center.center.y + math.cos(math.radians(angle)) * (center.size * 2)) for angle in range(0, 360, 60)]
	# 	if ring > 0:
	# 		for p in range(len(points)):
	# 			hexes.append(points[p])
	# 			A = points[p]
	# 			B = points[p+1] if p < 5 else points[0]
	# 			xdiff = (A.x - B.x) / (ring + 1) 
	# 			ydiff = (A.y - B.y) / (ring + 1) 
	# 			for i in range(ringnum):
	# 				hexes.append(Point(A.x + (xdiff * i), A.y + (ydiff * i)))
	# 	else:
	# 		hexes = points

	# for hex in range(len(hexes)):
	# 	hexes[hex] = Hexagon.from_size_and_center(hex, size, hexes[hex].x, hexes[hex].y)

# def print_hexes():
# 	for i in hexes:
# 		print(i.index, [x.index if x is not None else None for x in i.tiles ])

generate_hexes(ringnum, size)


running = True
# running = False

if running:
	screen = pygame.display.set_mode(frame, pygame.RESIZABLE)
	pygame.init()

while running:
	current_time = time.time()
	elapsed_time = current_time - start_time


	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 2:
				startpoint = get_pos()
				drag = True
			if event.button == 5:
				scale *= 0.9

		elif event.type == pygame.MOUSEBUTTONUP:
			if event.button == 2:
				lastoffset = offset
				# offset = 0, 0
				drag = False
			if event.button == 4:
				scale *= 1.1

		elif event.type == pygame.MOUSEMOTION:
			if drag:
				cursorCursorOffset = tuple_subtract(get_pos(), startpoint)
				offset = tuple_add(cursorCursorOffset, lastoffset)

		if event.type == pygame.KEYDOWN:

			if event.key == pygame.K_ESCAPE:
				running = False

	if elapsed_time > 0.1:
		# hexagon = Hexagon.from_size_and_center(200, frame[0]/2, frame[1]/2)
		for q in hexes:
			for r in q:
				r.render(screen, width=2)
		pygame.display.update()
		screen.fill((0,0,0)) 
