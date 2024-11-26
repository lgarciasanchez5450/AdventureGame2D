from typing import final,Callable,Any,Generic,Generator,Iterable, Callable,TypeVar
from .Fast import njit
from math import cos, sin,pi,hypot,sqrt,atan2,floor,log2,ceil,acos,tanh
from random import random,randint
from collections import deque
import numpy as np

DEBUG = True
#define inclusive_range
def inclusive_range(start:int,stop:int,step:int) -> Generator[int,None,None]: #type: ignore
	yield from range(start,stop,step)
	yield stop

	
try:
	import entity_manager2  #type: ignore
	inclusive_range:Callable[[int,int,int],Generator[int,None,None]] = entity_manager2.inclusive_range

except:
	print('Entity Manager Module has not been compiled, defaulting back to pure python, this will slow down physics.')
def collide_chunks(x1:float,y1:float,z1:float,x2:float,y2:float,z2:float,chunk_size:int): # type: ignore[same-name]
	cx1 = (round(x1,4) / chunk_size).__floor__()
	cy1 = (round(y1,4) / chunk_size).__floor__()
	cz1 = (round(z1,4) / chunk_size).__floor__()
	cx2 = (round(x2,4) / chunk_size).__ceil__()
	cy2 = (round(y2,4) / chunk_size).__ceil__()
	cz2 = (round(z2,4) / chunk_size).__ceil__()
	return[(x,y,z) for x in range(cx1,cx2,1) for z in range(cz1,cz2,1) for y in range(cy1,cy2,1)]
def collide_chunks2d(x1:float,y1:float,x2:float,y2:float,chunk_size:int): # type: ignore[same-name]
	cx1 = (round(x1,4) / chunk_size).__floor__()
	cy1 = (round(y1,4) / chunk_size).__floor__()
	cx2 = (round(x2,4) / chunk_size).__ceil__()
	cy2 = (round(y2,4) / chunk_size).__ceil__()
	return [(x,y) for x in range(cx1,cx2,1) for y in range(cy1,cy2,1)]
try:
	raise ModuleNotFoundError()
	import entity_manager2 #type: ignore
	collide_chunks:Callable[[float,float,float,float,float,float,int],tuple[tuple[int,int,int],...]] = entity_manager2.collide_chunks #type: ignore
except (ModuleNotFoundError or ImportError) as err:
	print('Error Importing entity_manager2')

	




half_sqrt_2 = (2**(1/2))/2
TO_RADIANS = pi / 180
TO_DEGREES = 180 / pi
TWO_PI = 2*pi

T = TypeVar("T")



@njit(cache = True)
def restrainMagnitude(x:float,y:float,mag:float):
	sqrM =  x*x+y*y
	if sqrM > mag * mag:
		mult = mag/sqrt(sqrM)
		x *= mult
		y *= mult
	return x,y

def getNamesOfObject(object):
	return [local for local in dir(object) if not local.startswith('__')]

@njit(cache = True)
def randomNudge(x:float,y:float,nudgeMag:float): #this random nudge prefers smaller nudges than bigger ones
	#techincally it will nudge it more in the diagonal more than horiztonal since the nudge values are not normalized
	mag = sqrt(x*x+y*y)
	nudgeX = 2*random()-1
	nudgeY = 2*random()-1
	nudgeX, nudgeY = restrainMagnitude(nudgeX,nudgeY,1)
	x += nudgeMag * nudgeX
	y += nudgeMag * nudgeY
	return  set_mag(x,y,mag)
	

def getMostSigBits(x:int,n:int) -> int:
	'''Get n most significant bits of x '''
	return x >> max(0,x.bit_length() - n)

def serialIter(*iters:Iterable):
	for iter in iters:
		yield from iter

@njit
def manhattan_distance(x1,y1,x2,y2):
	return abs(x1-x2)+abs(y1-y2)

class Vector2Int:
	__slots__  = 'x','y'
	def __init__(self,x:int,y:int):
		self.x = x
		self.y = y

	@final
	@classmethod
	def zero(cls):
		return Vector2Int(0,0)
	
	def __eq__(self,__object: "Vector2Int"):
		return self.x == __object.x and self.y == __object.y
	
	def __add__(self,__object: "Vector2Int"):
		return Vector2Int(self.x + __object.x,self.y + __object.y)
	
	def __sub__(self,__object: "Vector2Int"):
		return Vector2Int(self.x - __object.x,self.y - __object.y)
	
	def __mul__(self,__object:int):
		return Vector2Int(self.x *__object,self.y * __object)
	
	def __rmul__(self,__object:int):
		return Vector2Int(self.x *__object,self.y * __object)
	
	def __itruediv__(self,__object:int):
		self.x /= __object
		self.y /= __object
		return self

	def __floordiv__(self,__object:int):
		return Vector2Int(self.x // __object, self.y // __object)
	
	def moved_by(self,x:int,y:int):
		return Vector2Int(self.x + x, self.y + y)
	
	def __matmul__(self,__object: "Vector2Int"):
		return Vector2Int(self.x*__object.x,self.y*__object.y)
	
	def __getitem__(self,__index:int) -> int:
		return [self.x,self.y][__index]
	
	def __iadd__(self,__object: "Vector2Int"):
		self.x += __object.x
		self.y += __object.y
		return self

	def __isub__(self,__object: "Vector2Int"):
		self.x -= __object.x
		self.y -= __object.y
		return self

	def __imul__(self,__object:int):
		self.x *= __object
		self.y *= __object
		return self

	def __str__(self) -> str:
		return f"Vec2Int(x:{self.x}, y:{self.y})"	
	
	def __neg__(self):
		return Vector2Int(-self.x,-self.y)

	
	def magnitude_squared(self):
		return self.x*self.x+self.y*self.y
	
	def magnitude(self):
		return sqrt(self.x*self.x + self.y * self.y)
	
	def reset(self):
		'''Reset each axis to 0'''
		self.x = 0
		self.y = 0

	def __bool__(self):
		return (self.x or self.y).__bool__()
	
	def __iter__(self):
		yield self.x
		yield self.y
	
	def set_to(self,__object:'Vector2Int'):
		self.x = __object.x
		self.y = __object.y

	@classmethod
	def newFromTuple(cls,tup:tuple[int,int]):
		return Vector2Int(tup[0],tup[1])
	def from_tuple(self,tup:tuple[int,int]):
		self.x = tup[0]
		self.y = tup[1]

	@property
	def tuple(self):
		return (self.x,self.y)

	def copy(self):
		return Vector2Int(self.x,self.y)

class Array(list,Generic[T]):
	@staticmethod
	def none_range(stop:int):
		a = -1
		while (a := a + 1) < stop:
			yield None
	@classmethod
	def new(cls,size:int):
		return cls(cls.none_range(size))
	
	def __getitem__(self,index:int) -> T|None:
		return super().__getitem__(index)
	def append(self, __object):
		return SyntaxError("Array Size cannot be changed")
	
	def insert(self, __index, __object):
		return SyntaxError("Array Size cannot be changed")

	def clear(self):
		return SyntaxError("Array Size cannot be changed")
	
	def extend(self, __iterable):
		return SyntaxError("Array Size cannot be changed")

	def pop(self, __index = -1):
		return SyntaxError("Array Size cannot be changed")

	def iadd(self,__object):
		return SyntaxError("Array Size cannot be changed")

	def remove(self,__index):
		'''Set a certain Index to None'''
		self[__index] = None

	def take(self,__index):
		item,self[__index] = self[__index],None
		return item

	def swap(self,__index,__object):
		item,self[__index] = self[__index],__object
		return item

	def swapIndices(self,__index1:int, __index2:int):
		self[__index1],self[__index2] = self[__index2],self[__index1]

class Counter(Generic[T]):
	__slots__ = 'obj','a','b'
	def __init__(self,obj1:T,a:float = 0.0,):
		self.obj = obj1
		self.a = a
		self.b = 0

	def __iter__(self):
		yield self.obj
		yield self.a
		yield self.b

	def __getitem__(self,__index:int):
		assert __index in (0,1), 'Counter only supports 0 and 1 as indexes'
		return self.b if __index else self.a

def make2dlist(x:int,y:int|None = None) -> tuple[list[None],...]:
	y = x if y is None else y
	return tuple([[None]*x for _ in range(y)])

@njit(cache = True)
def normalize(x,y) -> tuple[float,float]:
	mag = hypot(x,y)
	if mag == 0: return (0,0)
	else: return (x/mag,y/mag)

@njit(cache = True)
def set_mag(x,y,mag:int|float) -> tuple[float,float]:
	if x*x+y*y == 0: return (0,0)
	ux,uy = normalize(x,y)

	return  (ux*mag,uy*mag)

