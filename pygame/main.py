import pygame
import time
import math
import random
from math import sqrt
from pygame.mouse import get_pos
from collections import namedtuple
from shapely.geometry import Polygon

Cube = namedtuple('Cube', ['q', 'r', 's'])
Axel = namedtuple('Axel', ['q', 'r'])
tiles = namedtuple('tiles', ['n', 'ne', 'se', 's', 'sw', 'nw'])
Point = namedtuple('Point', ['x', 'y'])

size = 8
ringnum = 20
hexes = []

frame = 1792, 896

pygame.display.set_caption('killer')

start_time = time.time() - 0.5

offset = 1792/2, 896/2
scale = 1

drag = False
startpoint = 0, 0
lastoffset = offset

pieces = [
	"soldier",
	"farm",
	"tree",
	"HQ",
	"tower"
]

class Game:
	def __init__(self):
		self.hexes = []
		self.players = [Player(), Player(), Player(), Player(), Player()]

	def generate_map(self, ringnum, size):
		# for r in range(-ringnum, ringnum+1):
		# 	if r < 0:
		# 		for q in range(-(r+ringnum), 0):
		# 			self.hexes.append(Hexagon.from_axel(q, r, size))
		# 		for q in range(ringnum+1):
		# 			self.hexes.append(Hexagon.from_axel(q, r, size))
		# 	elif r == 0:
		# 		for q in range(-ringnum, ringnum+1):
		# 			self.hexes.append(Hexagon.from_axel(q, r, size))
		# 	elif r > 0:
		# 		for q in range(-ringnum, 0):
		# 			self.hexes.append(Hexagon.from_axel(q, r, size))
		# 		for q in range(ringnum-r+1):
		# 			self.hexes.append(Hexagon.from_axel(q, r, size))

		island = namedtuple('island', ['center', 'hexes', 'bridges'])
		island_num = 70
		map_boundary =  int(math.log(island_num+3, 1.2))
		island_min_rad = 2
		island_max_rad = 5
		island_random_point_chance = 0.40
		islands = []
		for i in range(island_num):

			is_hexes = []

			island_center = Axel(0, 0)
			greenlit = False
			while not greenlit and not len(islands) == 0:
				island_center = Axel(random.randint(-map_boundary,  map_boundary), random.randint(-map_boundary,  map_boundary))
				for center in islands:
					if island_center.q != center.center.q or island_center.r != center.center.r:
						greenlit = True

			is_hexes += axial_spiral(island_center, island_min_rad)

			# if i == 0 or i == 1:
			# 	island_center = Axel(0, 0)

			for ring in range(island_min_rad, island_max_rad):
				r = axial_ring(island_center, ring)
				points = random.choices(r, k=int(len(r)*island_random_point_chance))
				for point in points:
					line = axial_linedraw(island_center, point)
					for i in line:
						if is_hexes.count(i) == 0:
							is_hexes.append(i)
			islands.append(island(island_center, is_hexes, []))

		# for isl in islands:
		# 	distances = [0, 0, 0]
		# 	for i in islands:
		# 		if isl == i and i.bridges.count(isl) != 0:
		# 			continue

		# 		distance = axial_distance(i.center, isl.center)
		# 		if distance <= island_min_rad*2:
		# 			continue
		# 		if distance <= island_max_rad*2:
		# 			line = axial_linedraw(i.center, isl.center)
		# 			for hex in line:
		# 				if hex not in i.hexes and hex not in isl.hexes:
		# 					isl.hexes.append(hex)
		# 		else:
		# 			for dist in range(len(distances)):
		# 				if distance > distances[dist]:
		# 					distances.pop(2)
		# 					distances = distances[0:dist] + [distance] + distances[dist:2]
		# 					isl.bridges.pop(2)
		# 					isl = isl._replace(bridges=isl.bridges[0:dist] + [i] + isl.bridges[dist:2])

		linked = []

		for isl in islands:
			max_distance = 0
			for i in islands:
				if isl == i and i.bridges.count(isl) != 0:
					continue

				distance = axial_distance(i.center, isl.center)

				if distance <= island_min_rad*2:
					linked.append((isl, i))
					continue
				elif distance <= island_max_rad*2:
					linked.append((isl, i))
					line = axial_linedraw(i.center, isl.center)
					for hex in line:
						if hex not in i.hexes and hex not in isl.hexes:
							isl.hexes.append(hex)
					continue 
				else:
					isl = isl._replace(bridges=isl.bridges + [(i, distance)])

			isl = isl._replace(bridges=sorted(isl.bridges, key=lambda x: x[1]))
			if len(isl.bridges) > 3:
				isl = isl._replace(bridges=isl.bridges[:3])

			for i in isl.bridges:
				if i is None:
					continue
				line = axial_linedraw(i[0].center, isl.center)
				for hex in line:
					if hex not in i[0].hexes and hex not in isl.hexes:
						isl.hexes.append(hex)



		tree_chance = 0.05

		transferred_hexes = [Axel(0, 0)]
		for isl in islands:
			for i in isl.hexes:
				if not transferred_hexes.count(i):
					self.hexes.append(Hexagon.from_axel(i, size))
					transferred_hexes.append(i)
					if random.random() < tree_chance:
						self.hexes[-1].contains = "tree"

		provinces = 10
		spawndeterrent = 0.0005

		province_centers = [random.choice(self.hexes)]
		for i in range(provinces-1):
			greenlit = False
			hex = None
			while not greenlit:
				hex = random.choice(self.hexes)
				dist = axial_distance(province_centers[0].axel, hex.axel)
				for i in province_centers[0:]:
					new = axial_distance(province_centers[0].axel, hex.axel)
					if new < dist:
						dist = new
				if (rand := random.random()) < (spawndeterrent * dist):
					greenlit = True
				# print(dist, spawndeterrent * dist, rand, greenlit)
			province_centers.append(hex)

		for center in province_centers:
			if center is None:
				print("wtf pls no")
				continue
			center.contains = "HQ"
			prov = Province(center, self.get_hexes(axial_neighbors(center))+[center])
			player = self.players[province_centers.index(center) % len(self.players)]
			player.provinces.append(prov)
			prov.player = player
			prov.provincify(prov.tiles)
			print(prov.tiles)

			# self.players[]




		

		

	def render(self):
		for hex in self.hexes:
			w, h = pygame.display.get_surface().get_size()
			if -scale*size < hex.center.x * scale + offset[0] < w+scale*size and -scale*size < hex.center.y * scale + offset[1] < h+scale*size:
				hex.render(screen)

	def get_hex(self, axel):
		for x in self.hexes:
		    if axel.q == x.q and axel.r == x.r:
		    	return x

	def get_hexes(self, axels):
		hexes = []
		for axel in axels:
			for x in self.hexes:
			    if axel.q == x.q and axel.r == x.r:
			    	hexes.append(x)
			    	break
		return hexes



class Player:
	def __init__(self):
		self.provinces = []
		self.selected_town = None
		self.color = (random.randint(0, 256), random.randint(0, 256), random.randint(0, 256))

class Province:
	def __init__(self, HQ, tiles):
		self.HQ = HQ
		self.tiles = tiles
		self.cash = 0
		self.income = 0
		self.farms = 0
		self.trees = 0
		self.units = []
		self.player = None

	def provincify(self, hexes):
		for hex in range(len(hexes)):
			hexes[hex].province = self

	def deprovincify(self, hexes):
		for hex in range(len(hexes)):
			hexes[hex].province = None

class Hexagon:

	def __init__(self):
		self.index = -2
		self.q = 0
		self.r = 0
		self.points: list
		self.center: Point
		self.size: any
		self.axel: Axel

		self.enabled = True
		self.owner = None
		self.contains = None
		self.level = 0
		self.protection = 0
		self.selected = False
		self.province = None

	@staticmethod
	def from_axel(axel, size):
		poly = Hexagon()
		poly.axel = axel
		poly.q = poly.axel.q
		poly.r = poly.axel.r
		poly.center = Point(round(1.1*size * (3./2 * poly.q), 3), round(1.1*size * (sqrt(3)/2 * poly.q + sqrt(3) * poly.r), 3))
		poly.points = [Point(round(poly.center.x + math.cos(math.radians(angle)) * size, 3), round(poly.center.y + math.sin(math.radians(angle)) * size, 3)) for angle in range(0, 360, 60)]
		poly.size = size
		return poly

	def render(self, screen):
		if self.province is None:
			color = (128, 128, 128)
		else:
			color = self.province.player.color

		points = [(((i.x*scale) + offset[0]), ((i.y*scale) + offset[1])) for i in self.points]
		pygame.draw.polygon(screen, color, points)
		side = scale*size
		if self.level:
			rec = pygame.Rect((points[2][0], points[2][1]-(side/3)), (side/4*self.level, side/3))
			screen.fill((153, 153, 0), rec)
		if self.contains == "soldier":
			where_you_hold_the_axe_i_cant_remember_the_term = pygame.Rect((points[2][0]+side/3, points[4][1]+side/5), (side/10, side))
			blade = [(points[4][0]+side/10, points[4][1]+side/2),
						(points[5][0]-side/5, points[0][1]),
						(points[5][0]-side/5, points[5][1]+side/5)]
			screen.fill((153, 76, 0), where_you_hold_the_axe_i_cant_remember_the_term)
			pygame.draw.polygon(screen, (80, 80, 80), blade)
		if self.contains == "tree":
			stem = pygame.Rect((points[2][0]+(side/5*2), points[3][1]), (side/5, side/2))
			bush = pygame.Rect((points[4][0], points[5][1]+(side/3)), (side, side/5*4))
			screen.fill((153, 76, 0), stem)
			screen.fill((0, 153, 0), bush)
		if self.contains == "tower":
			stem = pygame.Rect((points[2][0]+(side/4), points[3][1]-(side/2)), (side/2, side))
			top = pygame.Rect((points[2][0], points[4][1]+(side/3)), (side, side/4))
			teeth = [
				pygame.Rect((points[4][0], points[4][1]+(side/5)), (side/5, side/5)),
				pygame.Rect((points[4][0]+(side/5*2), points[4][1]+(side/5)), (side/5, side/5)),
				pygame.Rect((points[4][0]+(side/5*4), points[4][1]+(side/5)), (side/5, side/5)),
			]
			screen.fill((80, 80, 80), stem)
			screen.fill((50, 50, 50), top)
			for i in teeth:
				screen.fill((50, 50, 50), i)
		if self.contains == "farm":
			trapez = [(points[0][0]-(side/4), points[0][1]), (points[4][0] - (side/4), points[0][1]), (points[4][0]+(side/4), points[4][1]+side/4), (points[5][0]-(side/4), points[5][1]+side/4)]
			base = pygame.Rect((points[2][0], points[0][1]), (side, side/2))
			screen.fill((153, 76, 0), base)
			pygame.draw.polygon(screen, (229, 209, 107), trapez)
		if self.contains == "HQ":
			trapez = [(points[0][0]-(side/4), points[0][1]), (points[4][0] - (side/4), points[0][1]), (points[4][0]+(side/4), points[4][1]+side/4), (points[5][0]-(side/4), points[5][1]+side/4)]
			base = pygame.Rect((points[2][0], points[0][1]), (side, side/2))
			cimney = pygame.Rect((points[5][0]-(side/3), points[5][1]+(side/4)), (side/4, side/2))
			screen.fill((153, 76, 0), base)
			pygame.draw.polygon(screen, (229, 209, 107), trapez)
			screen.fill((100, 100, 100), cimney)
		# pygame.draw.polygon(screen, (0, 0, 0), points, width)

	def __str__(self):
		return f"(q={self.q}, r={self.r}) {self.level}"

def cube_round(frac):
    q = round(frac.q)
    r = round(frac.r)
    s = round(frac.s)

    q_diff = abs(q - frac.q)
    r_diff = abs(r - frac.r)
    s_diff = abs(s - frac.s)

    if q_diff > r_diff and q_diff > s_diff:
        q = -r-s
    elif r_diff > s_diff:
        r = -q-s
    else:
        s = -q-r

    return Cube(q, r, s)

def cube_to_axial(cube):
    q = cube.q
    r = cube.r
    return Axel(q, r)

def axial_to_cube(hex):
    q = hex.q
    r = hex.r
    s = -q-r
    return Cube(q, r, s)

axial_direction_vectors = [
    Axel(+1, 0), Axel(+1, -1), Axel(0, -1), 
    Axel(-1, 0), Axel(-1, +1), Axel(0, +1), 
]

def axial_direction(direction):
    return axial_direction_vectors[direction]

def axial_add(hex, vec):
    return Axel(hex.q + vec.q, hex.r + vec.r)

def axial_neighbor(hex, direction):
    return axial_add(hex, axial_direction(direction))

def axial_neighbors(hex):
	n = []
	for i in axial_direction_vectors:
		n.append(axial_add(hex, i))
	return n

def axial_scale(hex, factor):
    return Axel(hex.q * factor, hex.r * factor)

def axial_ring(center, radius):
    results = []
    # this code doesn't work for radius == 0; can you see why?
    hex = axial_add(center, axial_scale(axial_direction(4), radius))
    for i in range(0, 6):
        for _ in range(0, radius):
            results.append(hex)
            hex = axial_neighbor(hex, i)
    return results

def axial_spiral(center, radius):
    results = [center]
    for k in range(1, radius+1):
        results += axial_ring(center, k)
    return results

def lerp(a, b, t): # for floats
    return a + (b - a) * t

def axial_distance(a, b):
    return int((abs(a.q - b.q) 
              + abs(a.q + a.r - b.q - b.r)
              + abs(a.r - b.r)) / 2)

def axial_round(hex):
    return cube_to_axial(cube_round(axial_to_cube(hex)))

def axial_lerp(a, b, t): # for hexes
    return Axel(lerp(a.q, b.q, t),
                lerp(a.r, b.r, t))

def axial_linedraw(a, b):
    N = axial_distance(a, b)
    results = []
    for i in range(0, N+1):
        results.append(axial_round(axial_lerp(a, b, 1.0/N * i)))
    return results


def tuple_add(tuple1, tuple2):
	return tuple1[0] + tuple2[0], tuple1[1] + tuple2[1]

def tuple_subtract(tuple1, tuple2):
	return tuple1[0] - tuple2[0], tuple1[1] - tuple2[1]

def tuple_factor(tuple1, factor):
	return tuple1[0] * factor, tuple1[1] * factor

def point_are_close(a, b):
	return (math.isclose(a.x, b.x) and math.isclose(a.y, b.y))

game = Game()
game.generate_map(ringnum, size)
# for i in game.hexes:
# 	print(i)

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
		game.render()
		# hexagon = Hexagon.from_size_and_center(200, frame[0]/2, frame[1]/2)

		pygame.display.update()
		screen.fill((0,0,0)) 
