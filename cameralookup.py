from Tkinter import Tk, Canvas, Frame, BOTH, N, S, E, W, Scrollbar, VERTICAL, HORIZONTAL
import Tkinter
import math
import pickle

screenSize = [600,600]
canvasSize = [2000,2000]

class fieldOfView:
	
	def initAll(self):
		self.initHandles()
		# The location of the camera, 0-999
		self.loc = [100,100]
		# The logical camera number
		self.cam_num = 1001
		# The preset of this view, if it's a PTZ camera
		self.preset = 0
		# A list of the coordinates of the view, relative to the camera's coordinates
		self.view = [[50,1],[1,200],[200,200],[100,1]]
		# A list of the blind spots in the view, relative to the camera's coordinates
		self.blinds = [[[60,60],[100,60],[100,100],[60,100]]]
		self.blindCount = len(self.blinds)
		# The handle of the view polygon
		self.viewHandle = 0
		# The handles of the corner circles of the view
		self.viewCornersHandles = []
		# The handles of the blind spot polygons
		self.blindHandles = []
		# The handles of the blind spot polygon corner circles
		self.blindCornersHandles = [[]]
		# The camera circle handle
		self.cameraHandle = 0
		self.cameraSize = 15
		# The size of the corner handle circles
		self.handleSize = 10
		self.lineThickness = 2
		self.init = 1
	
	def initHandles(self):
		self.viewHandle = 0
		self.cameraHandle = 0
		self.viewCornersHandles = []
		self.blindHandles = []
		self.blindCornersHandles = [[]]
		
	
	def handleCheck(self, myHandle):
		# This function checks if the supplied canvas handle corresponds to anything this class owns
		if myHandle == self.cameraHandle:
			return True
		if myHandle in self.viewCornersHandles:
			return True
		for i in range(self.blindCount):
			if myHandle in self.blindCornersHandles[i]:
				return True
		return False
		
	def getHandleFromCoords(self, coords):
		# This function returns the handle number of a corner circle if it encompasses the supplied coordinates
		
		if coordDistance(coords, self.loc) < self.cameraSize/2:
			return self.cameraHandle
		
		# Translate to camera-centric coordinates
		coords[0] -= self.loc[0]
		coords[1] -= self.loc[1]
		
		for i in range(len(self.view)):
			if coordDistance(coords, self.view[i]) < self.handleSize/2:
				return self.viewCornersHandles[i]
		
		for j in range(self.blindCount):
			for i in range(len(self.blinds[j])):
				if coordDistance(coords, self.blinds[j][i]) < self.handleSize/2:
						return self.blindCornersHandles[j][i]
		return 0
		
	def updateCoord(self, myHandle, coord):
		# This function is used to instruct this class that one of its handles has moved
		# Translate to camera-centric coordinates
		if (min(coord) < 0) or (coord[0] > canvasSize[0]) or (coord[1] > canvasSize[1]):
			return False
		if not self.handleCheck(myHandle):
			return False
		if myHandle == self.cameraHandle:
			self.loc = coord
			return True
		coord[0] -= self.loc[0]
		coord[1] -= self.loc[1]
		if myHandle in self.viewCornersHandles:
			self.view[self.viewCornersHandles.index(myHandle)] = coord
			return True
		for i in range(self.blindCount):
			if myHandle in self.blindCornersHandles[i]:
				self.blinds[i][self.blindCornersHandles[i].index(myHandle)] = coord
				return True
		self.init = 0
	
	def inFoV(self, coordToCheck):
		# This function checks if the provided coordinate is within the field's view
		# Transform the coord into camera-centric coordinates
		coordToCheck[0] -= loc[0]
		coordToCheck[1] -= loc[1]
		# Check if the coord is inside this view
		if not point_inside_polygon(coordToCheck[0],coordToCheck[1], view):
			return False
		# Check to see whether it's also inside a blindspot
		for i in range(blindCount):
			if point_inside_polygon(coordToCheck[0],coordToCheck[1], blinds[i]):
				return False
		return True

	def draw(self, myCanvas):
		self.initHandles()
		points = []
		
		self.cameraHandle = myCanvas.create_oval(	self.loc[0]-self.cameraSize/2,
													self.loc[1]-self.cameraSize/2,
													self.loc[0]+self.cameraSize/2,
													self.loc[1]+self.cameraSize/2,
													outline='purple',fill='purple')
		
		for i in range(len(self.view)):
			points.append(self.view[i][0]+self.loc[0])
			points.append(self.view[i][1]+self.loc[1])
			self.viewCornersHandles.append(myCanvas.create_oval(self.view[i][0]+self.loc[0]-self.handleSize/2,
																self.view[i][1]+self.loc[1]-self.handleSize/2,
																self.view[i][0]+self.loc[0]+self.handleSize/2,
																self.view[i][1]+self.loc[1]+self.handleSize/2,
																outline='green',fill='green'))
		self.viewHandle = myCanvas.create_polygon(points, outline='green',fill='',width=self.lineThickness)
		
		
		for j in range(self.blindCount):
			points = []
			for i in range(len(self.blinds[j])):
				self.blindCornersHandles.append([])
				points.append(self.blinds[j][i][0]+self.loc[0])
				points.append(self.blinds[j][i][1]+self.loc[1])
				self.blindCornersHandles[j].append(myCanvas.create_oval(self.blinds[j][i][0]+self.loc[0]-self.handleSize/2,
																		self.blinds[j][i][1]+self.loc[1]-self.handleSize/2,
																		self.blinds[j][i][0]+self.loc[0]+self.handleSize/2,
																		self.blinds[j][i][1]+self.loc[1]+self.handleSize/2,
																		outline='red',fill='red'))
			self.blindHandles.append(myCanvas.create_polygon(points, outline='red',fill='',width=self.lineThickness))
		'''print self.viewHandle
		print self.viewCornersHandles
		print self.blindHandles		
		print self.blindCornersHandles'''
		
	def __init__(self):
		self.initAll()
		print "Butts"

def coordDistance(coord1, coord2):
	return math.sqrt( ( coord1[0]-coord2[0] )**2 + ( coord1[1]-coord2[1] )**2 )

def point_inside_polygon(x,y,poly):
	# http://geospatialpython.com/2011/01/point-in-polygon.html
	n = len(poly)
	inside =False

	p1x,p1y = poly[0]
	for i in range(n+1):
		p2x,p2y = poly[i % n]
		if y > min(p1y,p2y):
			if y <= max(p1y,p2y):
				if x <= max(p1x,p2x):
					if p1y != p2y:
						xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
					if p1x == p2x or x <= xinters:
						inside = not inside
		p1x,p1y = p2x,p2y

	return inside
	
class Example(Frame):
	canvas = 0
	handle = 0
	editFov = 0
	callbackLock = 0
	fov = []
	
	def __init__(self, parent):
		Frame.__init__(self, parent)
		
		#self.fov.append(fieldOfView())
		try:
			self.loadFromFile()
		except IOError:
			self.fov.append(fieldOfView())
			self.saveToFile()

		#print self.fov
		self.parent = parent		
		self.initUI()
		
		
	def initUI(self):
		self.parent.title("Shapes")		
		self.pack(fill=BOTH, expand=1)
		#self.pack(fill=BOTH, expand=1)

		#self.canvas = Canvas(self,width=canvasSize[0],height=canvasSize[1])
		#self.canvas.config(scrollregion = (0,0,canvasSize[0],canvasSize[1]))

		self.canvas = Canvas(self)
		hScroll = Scrollbar(self, orient="h", command=self.canvas.xview)
		vScroll = Scrollbar(self, orient="v", command=self.canvas.yview)
		self.canvas.configure(yscrollcommand=vScroll.set, xscrollcommand=hScroll.set)
		
		self.canvas.grid(row=0,column=0,sticky="nsew")
		hScroll.grid(row=1, column=0, stick="ew")
		vScroll.grid(row=0, column=1, sticky="ns")
		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(0, weight=1)
		self.canvas.configure(scrollregion = (0, 0, canvasSize[0], canvasSize[1]))
		
		#the scrollbar for that canvas
		#self.vscroll = Scrollbar(self, orient = VERTICAL, command = self.canvas.yview )
		#self.vscroll.grid(column = 1, row = 0, sticky = N+S+E)
		#self.canvas["yscrollcommand"] = self.vscroll.set
		
		self.draw()
		self.canvas.focus_set()
		self.canvas.bind("<Key>", self.keyCallback)
		self.canvas.bind("<Button-1>", self.clickCallback)
		self.canvas.bind("<Button1-ButtonRelease>", self.releaseCallback)
		
		#self.canvas.bind("<Button1-Motion>", self.moveCallback)
		
		#self.canvas.pack(fill=BOTH, expand=1)
		
	def clickCallback(self, event):
		if self.callbackLock == 1:
			return
		else:
			self.callbackLock = 1
		#print "Woo!"+str(event.widget.find_closest(event.x, event.y)[0])
		for i in range(len(self.fov)):
			self.handle = self.fov[i].getHandleFromCoords([event.x,event.y])
			if self.handle != 0:
				self.editFov = i
				break
		self.callbackLock = 0
			
	def releaseCallback(self, event):
		if self.callbackLock == 1:
			return
		else:
			self.callbackLock = 1
		self.fov[self.editFov].updateCoord(self.handle,[event.x,event.y])
		self.draw()
		self.saveToFile()
		self.callbackLock = 0
		
	def keyCallback(self, event):
		if self.callbackLock == 1:
			return
		else:
			self.callbackLock = 1
		if event.char == 'a':
			print "Adding"
			self.fov.append(fieldOfView())
			self.draw()
			self.saveToFile()
		elif event.char == 'q':
			self.saveToFile()
			quit()
			
		self.callbackLock = 0
		
	def loadFromFile(self):
		print "Loading"
		f = open('views.sav', 'r')
		#stream = f.read()
		#self.fov = jason.loads(stream)
		self.fov = pickle.load(f)
		f.close()
	
	def saveToFile(self):
		f = open('views.sav', 'w')
		#stream = json.dumps(self.fov)
		pickle.dump(self.fov, f)
		#f.write(stream)
		f.close()		
		print "Saving"
		
	def draw(self):
		#for i in range(10000):
		#	self.canvas.delete(i)
		self.canvas.delete('all')
		for i in range(len(self.fov)):
			self.fov[i].draw(self.canvas)
		
		
		
def main():
	root = Tk()
	ex = Example(root)
	root.geometry(str(screenSize[0])+"x"+str(screenSize[1])+"+100+100")
	root.mainloop()  


if __name__ == '__main__':
	main()  