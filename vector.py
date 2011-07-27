import math

class Vector:
	
	def __init__(self,x,y):
		self.x = float(x)
		self.y = float(y)
	
	def magnitude(self):
		return (self.x**2 + self.y**2)**(.5)
		
	def __add__(self, othervector):
		return Vector(self.x + othervector.x, self.y + othervector.y)
		
	def __mul__(self, scalar):
		return Vector(self.x * scalar, self.y * scalar)
	
	def __div__(self, scalar):
		return Vector(self.x / scalar, self.y / scalar)
		
	def __sub__(self, othervector):
		return Vector(self.x - othervector.x, self.y - othervector.y)
		
	def normalize(self):
		mag = self.magnitude()
		self.x = self.x / mag
		self.y = self.y / mag
		
	def to_string(self, precision = 0):
		if precision:
			e = 10**precision
			componentA = math.floor(e * self.x) / e
			componentB = math.floor(e * self.y) / e
		else:
			componentA = self.x
			componentB = self.y
		return "<"+str(componentA)+","+str(componentB)+">"
		
	def __str__(self, precision = 0):
		return "<"+str(self.x)+","+str(self.y)+">"
	
	def __repr__(self):
		return "<"+str(self.x)+","+str(self.y)+">"
		
	def limitvalues(self,xmin,xmax,ymin,ymax):
		self.vel.x = max(xmin,min(xmax,self.vel.x))
		self.vel.y = max(ymin,min(ymax,self.vel.y))

