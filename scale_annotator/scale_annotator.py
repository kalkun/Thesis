import tkinter as tk
import os
from PIL import ImageTk, Image
import protestDB.models as models


class Annotator:
	"""
	This class implements a very simplistic GUI interface for labeling images. The current commands are the following:
	Unrelated - Space
	For giving a label for protest related images: number between 0 - 10
	Going back - b
	"""

	def __init__(self, img_folder, dbcursor):
		self.pc = dbcursor
		self.instructions = "Welcome to the annotator tool. These are the keyboard commands for labeling:" + \
		"\n" + "Space: unrelated" + "\n" + "For protest related images: a number between 0 - 10"
		self.folder = img_folder
		self.imgs = self.getImagesFromDB()
		#self.imgs_names = [x.name for x in self.imgs] # get a list of names
		print(len(self.imgs))
		self.current_image_index = -1
		self.initializeWindow()

	def getImagesFromDB(self):
		"""
		gets the images objects from the database by filtering only Luca Rossi as source
		and that do not currently hold a label in protest vs non protest
		"""
		q = self.pc.query(models.Images).outerjoin(
			models.ProtestNonProtestVotes, 
			models.ProtestNonProtestVotes.imageID== models.Images.imageHASH).\
		filter(models.ProtestNonProtestVotes.imageID == None).\
		filter(models.Images.source == 'Luca Rossi - ECB')
		return q.all()


	def initializeWindow(self):
		"""
		Initializes a window containing a image label and an instruction label and 
		starts the windowmain loop, which listen to events
		"""
		self.window = tk.Tk()
		w, h = self.window.winfo_screenwidth(), self.window.winfo_screenheight()
		self.window.geometry("%dx%d+0+0" % (w, h))
		self.window.title("scale annotator")
		self.window.bind("<Key>", self.keyboardCommand)
		self.img_label = tk.Label(self.window)
		self.instructions_label = tk.Label(text = self.instructions, font=("Helvetica", 16))
		self.instructions_label.pack()
		self.window.mainloop()

	def keyboardCommand(self, event):
		"""
		Defines what to do when a keyboard key is pressed 
		"""
		
		string_repr = repr(event.char)
		print(string_repr)
		if (string_repr == '\' \''):
			self.labelImage(True)
			self.nextImage()
		elif(string_repr == '\'\\r\''):
			self.labelImage(False)
			self.nextImage()
		elif (string_repr == '\'b\''):
			self.previousImage()

	def labelImage(self, label):
		pass

	def nextImage(self):
		"""
		Advance to the next image in terms of index 
		"""
		if (self.current_image_index >= len(self.imgs)):
			print("you reached the end of the images")
			return
		self.current_image_index += 1
		self.loadImage()
		

	def previousImage(self):
		"""
		Advance to the previous image in terms of index
		"""
		if (self.current_image_index <= 0):
			print("no previous image")
			return
		self.current_image_index += -1
		self.loadImage()


	def loadImage(self):
		"""
		Loads the current image and resize it if it does not fit the window
		"""
		path = os.path.join(self.folder, self.imgs[self.current_image_index].name)
		img = Image.open(path)
		width, height = img.size
		if (width > self.window.winfo_width()):
			print("resizing width")
			width = self.window.winfo_width()
		if (height > self.window.winfo_height()):
			print("resizing height")
			height = self.window.winfo_height()

		img = img.resize((width, height))
		self.img_label.img = ImageTk.PhotoImage(img)
		self.img_label.config(image = self.img_label.img)
		self.img_label.pack()



