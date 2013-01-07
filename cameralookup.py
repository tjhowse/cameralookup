#from Tkinter import Tk, Canvas, Frame, BOTH, N, S, E, W, Scrollbar, VERTICAL, HORIZONTAL
from Tkinter import *
import math
import pickle
#import ImageTk
import tkSimpleDialog
from PIL import ImageTk, Image

screenSize = [600,600]
canvasSize = [5000,5000]

class fieldOfView:
	
	def initAll(self, coords):
		self.initHandles()
		# The location of the camera, 0-999
		self.loc = coords
		# The logical camera number
		self.cam_num = 1001
		# The preset of this view, if it's a PTZ camera
		self.preset = 0
		# A list of the coordinates of the view, relative to the camera's coordinates
		self.view = [[50,1],[1,200],[200,200],[100,1]]
		# A list of the blind spots in the view, relative to the camera's coordinates
		#self.blinds = [[[60,60],[100,60],[100,100],[60,100]]]
		self.blinds = [[[]]]
		self.blindCount = 0
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
		self.selected = 0
	
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
		grabability = 1
		# This function returns the handle number of a corner circle if it encompasses the supplied coordinates
		
		if coordDistance(coords, self.loc) < self.cameraSize/grabability:
			return self.cameraHandle
		
		# Translate to camera-centric coordinates
		coords[0] -= self.loc[0]
		coords[1] -= self.loc[1]
		
		for i in range(len(self.view)):
			if coordDistance(coords, self.view[i]) < self.handleSize/grabability:
				return self.viewCornersHandles[i]
		if self.blindCount != 0:
			for j in range(self.blindCount):
			#for blind in self.blinds:
				for i in range(len(self.blinds[j])):
				#for corner in blind:			
					if coordDistance(coords, self.blinds[j][i]) < self.handleSize/grabability:
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
		# This function draws a view's polygon and blindspots
		self.initHandles()
		points = []
		
		if self.selected == 1:
			myViewOutline = 'green'
			myViewFill = ''
			myViewCornerOutline = 'green'
			myViewCornerFill = 'green'
			myBlindOutline = 'red'
			myBlindFill = ''
			myBlindCornerOutline = 'red'
			myBlindCornerFill = 'red'
			myCameraOutline = 'purple'
			myCameraFill = 'purple'
		else:
			
			myViewOutline = 'dark green'
			myViewFill = ''
			myViewCornerOutline = 'dark green'
			myViewCornerFill = 'dark green'
			myBlindOutline = 'dark red'
			myBlindFill = ''
			myBlindCornerOutline = 'dark red'
			myBlindCornerFill = 'dark red'
			myCameraOutline = 'dark violet'
			myCameraFill = 'dark violet'
		# Draw the camera circle
		self.cameraHandle = myCanvas.create_oval(	self.loc[0]-self.cameraSize/2,
													self.loc[1]-self.cameraSize/2,
													self.loc[0]+self.cameraSize/2,
													self.loc[1]+self.cameraSize/2,
													outline=myCameraOutline,fill=myCameraFill, tags='foreground')
		# Draw the view polygon, and circles at the corners
		for i in range(len(self.view)):
			points.append(self.view[i][0]+self.loc[0])
			points.append(self.view[i][1]+self.loc[1])
			self.viewCornersHandles.append(myCanvas.create_oval(self.view[i][0]+self.loc[0]-self.handleSize/2,
																self.view[i][1]+self.loc[1]-self.handleSize/2,
																self.view[i][0]+self.loc[0]+self.handleSize/2,
																self.view[i][1]+self.loc[1]+self.handleSize/2,
																outline=myViewCornerOutline,fill=myViewCornerFill, tags='foreground'))
		self.viewHandle = myCanvas.create_polygon(points, outline=myViewOutline,fill=myViewFill,width=self.lineThickness, tags='foreground')

		# Draw in the blind spot polygons and their corner circles
		for blind in self.blinds:
			if len(blind) < 4:
				break
			points = []
			for corner in blind:
				self.blindCornersHandles.append([])
				points.append(corner[0]+self.loc[0])
				points.append(corner[1]+self.loc[1])
				self.blindCornersHandles[-1][-1].append(myCanvas.create_oval(corner[0]+self.loc[0]-self.handleSize/2,
																		corner[1]+self.loc[1]-self.handleSize/2,
																		corner[0]+self.loc[0]+self.handleSize/2,
																		corner[1]+self.loc[1]+self.handleSize/2,
																		outline=myBlindCornerOutline,fill=myBlindCornerFill, tags='foreground'))
			self.blindHandles.append(myCanvas.create_polygon(points, outline=myBlindOutline,fill=myBlindFill,width=self.lineThickness, tags='foreground'))
		print self.blindCornersHandles
	def __init__(self, coords):
		self.initAll(coords)
		print "Butts"

def coordDistance(coord1, coord2):
	# This calculates the distance between two points on a cartesian plane.
	return math.sqrt( ( coord1[0]-coord2[0] )**2 + ( coord1[1]-coord2[1] )**2 )

def point_inside_polygon(x,y,poly):
	# This calculates whether a given point lies within a polygon.
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
	
class CameraLookup(Frame):
	canvas = 0
	handle = 0
	editFov = 0
	callbackLock = 0
	fov = []
	background = 0
	dragcoords = []
	clickCoords = []
	listSelection = None
	
	def __init__(self, parent):
		Frame.__init__(self, parent)
		try:
			self.loadFromFile()
		except IOError:
			self.fov.append(fieldOfView())
			self.saveToFile()

		self.parent = parent		
		self.initUI()
		
		
	def initUI(self):
		# This function sets up the window.
		self.parent.title("Camera Lookup")		
		self.pack(fill=BOTH, expand=1)

		#self.canvas = Canvas(self,width=canvasSize[0],height=canvasSize[1])
		#self.canvas.config(scrollregion = (0,0,canvasSize[0],canvasSize[1]))

		self.viewListbox = Listbox(self, selectmode=BROWSE)
		viewListboxScroll = Scrollbar(self, orient="v", command=self.viewListbox.yview)
		self.viewListbox.configure(yscrollcommand=viewListboxScroll.set)
		
		self.canvas = Canvas(self)
		self.canvas.pack(fill=BOTH,expand=1)
		hScroll = Scrollbar(self, orient="h", command=self.canvas.xview)
		vScroll = Scrollbar(self, orient="v", command=self.canvas.yview)
		self.canvas.configure(yscrollcommand=vScroll.set, xscrollcommand=hScroll.set)
		
		self.viewListbox.grid(row=0, column=1, sticky="nsew")
		viewListboxScroll.grid(row=0, column=0, sticky="ns")
		self.canvas.grid(row=0,column=2,sticky="nsew")
		hScroll.grid(row=1, column=2, stick="ew")
		vScroll.grid(row=0, column=3, sticky="ns")
		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(2, weight=1)
		self.canvas.configure(scrollregion = (0, 0, canvasSize[0], canvasSize[1]),xscrollincrement=1,yscrollincrement=1)
		
		self.background = ImageTk.PhotoImage(file="bg_5k.png")
		self.canvas.create_image(0, 0, image = self.background, anchor = NW)
		
		self.draw()
		#self.canvas.focus_set()
		
		self.canvas.bind("<Key>", self.keyCallback)
		self.canvas.bind("<Button-1>", self.clickCallback)
		self.canvas.bind("<Button1-ButtonRelease>", self.releaseCallback)
		
		self.canvas.bind("<Button-3>", self.rclickCallback)
		self.canvas.bind("<Button3-ButtonRelease>", self.rreleaseCallback)
		
		self.poll()
		#self.canvas.bind("<Button1-Motion>", self.moveCallback)
		
		#self.canvas.pack(fill=BOTH, expand=1)
		
	def rclickCallback(self, event):
		# This handles the right click event, and stores the coordinates to begin a drag
		self.dragcoords = [event.x, event.y]
	
	def rreleaseCallback(self, event):
		# This handles the right click release, completing a drag
		self.canvas.xview_scroll(-(event.x-self.dragcoords[0]), UNITS)
		self.canvas.yview_scroll(-(event.y-self.dragcoords[1]), UNITS)
		#self.canvas.yview += int(event.y)-self.dragcoords[1]
		#self.canvas.configure(yscrollcommand=vScroll.set, xscrollcommand=hScroll.set)
	
	def clickCallback(self, event):
		# This handles a left click, and works out what was clicked.
		if self.callbackLock == 1:
			return
		else:
			self.callbackLock = 1
		#print "Woo!"+str(event.widget.find_closest(event.x, event.y)[0])
		for i in range(len(self.fov)):
			self.handle = self.fov[i].getHandleFromCoords([event.x+self.canvas.canvasx(0),event.y+self.canvas.canvasy(0)])
			if self.handle != 0:
				self.selectView(i)
				break
		
		self.callbackLock = 0
		self.clickCoords = [event.x, event.y]
		
	def selectView(self, index):
		print "Deselecting index: "+str(self.editFov)+" Selecting index: "+str(index)
		self.deselectAll();
		self.editFov = index
		self.fov[self.editFov].selected = 1
		#self.viewListbox.selection_clear(0,END)
		self.viewListbox.selection_set(self.editFov)
		#self.draw()

	def deselectAll(self):
		for i in range(len(self.fov)):
			self.fov[i].selected = 0
			
	def releaseCallback(self, event):
		# This handles the left click release, carrying out the left click drag to reposition a circle
		if self.callbackLock == 1:
			return
		else:
			self.callbackLock = 1
		
		if self.clickCoords != [event.x, event.y]:
			self.fov[self.editFov].updateCoord(self.handle,[event.x+self.canvas.canvasx(0),event.y+self.canvas.canvasy(0)])
			self.saveToFile()
			
		self.draw()			
		self.callbackLock = 0
		
	def keyCallback(self, event):
		# This handles keyboard keypresses.
		print "Keypressed"
		if self.callbackLock == 1:
			print "locked"
			return
		else:
			self.callbackLock = 1
		if event.char == 'a':
			newCamNum = tkSimpleDialog.askinteger("New camera", "New camera number:", initialvalue = 1001)
			newCamPreset = tkSimpleDialog.askinteger("New camera", "New preset number:", initialvalue = 1)
			self.fov.append(fieldOfView([self.canvas.canvasx(0)+100,+self.canvas.canvasy(0)+100]))
			self.fov[-1].cam_num = newCamNum
			self.fov[-1].preset = newCamPreset
			self.selectView(len(self.fov)-1)
			self.draw()
			self.saveToFile()
		elif event.char == 'd':
			if self.editFov >= 0:
				print "Deleting: "+str(self.editFov)
				del self.fov[self.editFov]
				self.selectView(0)
				self.draw()
		elif event.char == 'q':
			self.saveToFile()
			quit()
			
		self.callbackLock = 0
		
	def loadFromFile(self):
		# This loads a list of views into memory from a file.
		f = open('views.sav', 'r')
		self.fov = pickle.load(f)
		f.close()
	
	def saveToFile(self):
		# This saves the current list of views to a file.
		f = open('views.sav', 'w')
		pickle.dump(self.fov, f)
		f.close()		
		print "Saved."
		
	def draw(self):
		# This draws all the views.
		
		self.viewListbox.delete(0,END)
		
		self.canvas.delete('foreground')
		for i in range(len(self.fov)):
			self.fov[i].draw(self.canvas)
			self.viewListbox.insert(END,str(self.fov[i].cam_num) + "-" + str(self.fov[i].preset))

		self.viewListbox.selection_set(self.editFov)
		self.canvas.focus_set()

	def poll(self):
		# This is a grotty hack to track changes in the selected item in the list
		current_selection = self.viewListbox.curselection()
		if len(current_selection) == 0:
			self.after(250,self.poll);
			return
		if int(current_selection[0]) != self.editFov:
			self.selectView(int(current_selection[0]))
			self.canvas.xview_moveto(((self.fov[self.editFov].loc[0]-(self.canvas.winfo_width()/2))/canvasSize[0]))
			self.canvas.yview_moveto(((self.fov[self.editFov].loc[1]-(self.canvas.winfo_height()/2))/canvasSize[1]))
			self.draw()
		self.after(250,self.poll);
		
def main():
	root = Tk()
	ex = CameraLookup(root)
	root.geometry(str(screenSize[0])+"x"+str(screenSize[1])+"+100+100")
	root.mainloop()  


if __name__ == '__main__':
	main()  