import pygame, os, sys, math, random, copy
from vector import Vector
# Everything should be calculated relative to rocket.

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((1000,500),pygame.DOUBLEBUF | pygame.RESIZABLE)
pygame.display.set_caption('Gravitron')
screen.set_colorkey((0,0,0))

font = pygame.font.SysFont("Arial", 12)

def load_image(name, colorkey=None):
	fullname = os.path.join('data', name)
	try:
		image = pygame.image.load(fullname)
	except pygame.error, message:
		print 'Cannot load image:', name
		raise SystemExit, message
	image = image.convert_alpha()
	if colorkey is not None:
		if colorkey is -1:
		  colorkey = image.get_at((0,0))
		image.set_colorkey(colorkey, pygame.RLEACCEL)
	return image, image.get_rect()
AScale = 5
class Projectile( pygame.sprite.DirtySprite ):

	def __init__(self,imagename, vel = Vector(0,0), truePos = Vector(1000,1000), spin = 0, maxSpeed = 7, groups = (), fuel = 10000000):
		pygame.sprite.Sprite.__init__(self, groups)
		self.original, self.rect = load_image(imagename)
		self.vel = vel
		self.spin = 0
		self.image = self.original
		self.rotate(spin)
		self.true = truePos
		self.rect.center = (pygame.display.Info().current_w/2,pygame.display.Info().current_h/2)
		self.mask = pygame.mask.from_surface(self.image)
		self.maxSpeed = maxSpeed # of the projectiles
		self.fuel = fuel
		
	def update(self):
		self.true = self.true + self.vel
		# wrap around universe
		if self.true.x > 2000:
		  self.true.x -= 2000
		if self.true.y > 2000:
		  self.true.y -=2000
		if self.true.x < 0:
		  self.true.x += 2000
		if self.true.y < 0:
		  self.true.y += 2000
		self.fuel -= 1 # track of time
		if self.fuel == 0:
			self.kill()
		
		true_angle = math.atan2( self.vel.y, self.vel.x )
		if true_angle < 0:
			true_angle += 2 * math.pi
		spin = math.radians(self.spin + 90)
		rq_spin = math.degrees((spin - true_angle))
		self.rotate( 10000 / rq_spin**2 )
	
	def accelerate(self, acceleration):
		self.vel += acceleration
		mag = self.vel.magnitude()
		if mag > self.maxSpeed: # maximum speed
			self.vel = self.vel / mag * self.maxSpeed
		
	def backward(self):
		angle = math.radians(self.spin)
		self.accelerate(Vector(math.sin(angle)/AScale, math.cos(angle)/AScale))
	
	def forward(self):
		angle = math.radians(self.spin)
		self.accelerate(Vector(-math.sin(angle)/AScale, -math.cos(angle)/AScale))
	
	def rotate(self, degrees):
		self.spin = self.spin + degrees
		if self.spin > 360:
			self.spin -= 360
		if self.spin < 0:
			self.spin += 360
		c = self.rect.center
		self.image = pygame.transform.rotate(self.original, round(self.spin))
		self.rect = self.image.get_rect(center = c)
		self.dirty = 1
		self.mask = pygame.mask.from_surface(self.image)
		
	def move(self, dx,dy):
		self.rect.x += dx
		self.rect.y += dy
		
	def reset(self):
		self.true = Vector(1000,1000)
		self.vel = Vector(0,0)
		
	def scroll(self,rocket):
		p = self.true - rocket.true
		dx = round(p.x + pygame.display.Info().current_w/2)
		dy = round(p.y + pygame.display.Info().current_h/2)
		self.rect.center = (dx,dy)
		
class Planet( pygame.sprite.DirtySprite ):
	def __init__(self,radius,x,y, groups = ()):
		pygame.sprite.Sprite.__init__(self, groups)
		self.radius = radius
		self.image = pygame.Surface((2*radius,2*radius))
		self.image.set_colorkey((0,0,0))
		self.image = self.image.convert()
		color = (random.randint(100,200),random.randint(100,200),random.randint(100,200))
		self.rect = pygame.draw.circle(self.image,color,(radius,radius),radius)
		self.rect.center = (x,y)
		self.true = Vector(x,y)
		self.mask = pygame.mask.from_surface(self.image)
		
	def scroll(self,rocket):
		p = self.true - rocket.true
		dx = round(p.x + pygame.display.Info().current_w/2)
		dy = round(p.y + pygame.display.Info().current_h/2)
		self.rect.center = (dx,dy)
		
	def update(self):
		pass

# TODO: math stuff to calculate effect
def gravity(planets, xpos, ypos):
	ppos = Vector(xpos,ypos)
	all_force = Vector(0,0)
	for s in planets:
		spos = s.true
		direction = spos - ppos
		force = .5 * (s.radius**2)/ (direction.magnitude()**3)
		direction.normalize()
		all_force = all_force + (direction * force)
	return all_force

allSprites = pygame.sprite.RenderUpdates()
rocketSprites = pygame.sprite.Group()
planetSprites = pygame.sprite.Group()
rocket = Projectile("srocket.png",groups = (rocketSprites,allSprites))

# randomly generate planets
# needs to be less random, to prevent initial collisions and overlaps
for i in range(10):
	r = random.randint(50,125)
	x = random.randint(0,2000)
	y = random.randint(0,2000)
	Planet(r,x,y,(planetSprites,allSprites))

done = False
dirty_rects = []
clock = pygame.time.Clock()
gamestate = {"level":1}
universe = [2000,2000]

text = ["" for i in xrange(pygame.display.Info().current_h / 15)]
achievement_queue = []

mapArea = pygame.Rect(pygame.display.Info().current_w - 210,pygame.display.Info().current_h - 210,200,200)
mapImage = pygame.Surface((200,200))

missiles = []

while not done:
	
	mapImage.fill((10,20,10,50))
	mapImage = mapImage.convert_alpha()
	clock.tick(80)

	screen.fill((0,0,0,0))
	
	cols = pygame.sprite.groupcollide(rocketSprites, planetSprites, False, False).iteritems()
	for r, ps in cols:
		for p in ps:
		  if pygame.sprite.collide_mask(r,p):
			 r.kill()
	
	visible_planets = []
	screen_rect = screen.get_rect()
	for p in planetSprites:
		if screen_rect.colliderect(p.rect):
		  visible_planets.append(p)
	for projectile in rocketSprites:
		gravity_force = gravity(visible_planets, projectile.true.x, projectile.true.y)
		projectile.accelerate(gravity_force)

	rocketSprites.update()
	for s in allSprites:
		if s != rocket:
			s.scroll(rocket)	
	
	dirty_rects = allSprites.draw(screen)

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
		  done = True
	key = pygame.key.get_pressed()
	if key[pygame.K_UP]:
		rocket.forward()
	if key[pygame.K_DOWN]:
		rocket.backward()
	if key[pygame.K_RIGHT]:
		rocket.rotate(-5)
	if key[pygame.K_LEFT]:
		rocket.rotate(5)
	if key[pygame.K_ESCAPE]:
		done = True
	if key[pygame.K_SPACE]:
		# shoot missile
		shoot = False
		if missiles:
			if missiles[-1].fuel < 250:
				shoot = True
		else:
			shoot = True
		if shoot:
			angle = math.radians(rocket.spin)
			direction = Vector(-math.sin(angle), -math.cos(angle))
			missiles.append(Projectile("srocket.png", direction * 10, rocket.true, rocket.spin, 10, (rocketSprites, allSprites), 500))


	text[0] = "Rocket is at " + rocket.true.to_string(3)
	text[1] = "Bearing: " + str((rocket.spin+90) % 360) + " degrees"
	text[2] = "Velocity: " + rocket.vel.to_string(3)
	text[3] = "G force: " + gravity_force.to_string(3)
	text[4] = "Level " + str(gamestate["level"])
	text[5] = ""
	text[6] = "Health: 100%"
	text[7] = "3 Enemies Left"
	text[9] = "FPS: " + str(clock.get_fps())
	text[-4] = "Achievement completed: Wormhole"
	text[-3] = "Achievement completed: Eliminate"
	text[-2] = "Achievement completed: Big Bang"
	text[-1] = "Level complete"
	for i,line in enumerate(text):
		if line != "":
		  textSurface = font.render(line, True, (39,255,20))
		  screen.blit(textSurface, (0,15*i))
		  dirty_rects.append(pygame.Rect(0,15*i,200,15))
	# map, TODO: draw enemies
	sf = universe[0]/mapArea.w
	scaled = rocket.true / sf
	pygame.draw.rect(mapImage, (255,255,255,255), pygame.Rect(scaled.x,scaled.y,5,5))
	for p in planetSprites:
		scaled = p.true / sf
		pygame.draw.circle(mapImage, (100,100,100,255), (int(scaled.x),int(scaled.y)), int(p.radius/sf))
	screen.blit(mapImage, mapArea)
	dirty_rects.append(mapArea)
	
	pygame.display.update(dirty_rects)

pygame.quit()

