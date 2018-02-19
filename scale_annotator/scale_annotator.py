import tkinter as tk
import os
from PIL import ImageTk, Image



class bidirectional_iterator(object):
    def __init__(self, collection):
        self.collection = collection
        self.index = 0

    def next(self):
        try:
        	self.index += 1
        	result = self.collection[self.index]
        except IndexError:
            raise StopIteration
        return result

    def prev(self):
        if self.index < 0:
            raise StopIteration
        else:
        	self.index -= 1
        return self.collection[self.index]

    def __iter__(self):
        return self


class Annotator:

	def __init__(self, img_folder):
		self.instructions = "Welcome to the annotator tool. These are the keyboard commands for labeling:" + \
		"\n" + "Space: unrelated" + "\n" + "For protest related images: a number between 0 - 10"
		self.folder = img_folder
		self.imgs_paths = bidirectional_iterator(os.listdir(img_folder))
		self.window = tk.Tk()
		w, h = self.window.winfo_screenwidth(), self.window.winfo_screenheight()
		self.window.geometry("%dx%d+0+0" % (w, h))
		self.window.title("scale annotator")
		self.window.bind("<Key>", self.label)
		self.img_label = tk.Label(self.window)
		self.instructions_label = tk.Label(text = self.instructions, font=("Helvetica", 16))
		self.instructions_label.pack()
		self.window.mainloop()

	def nextImage(self):
		path = os.path.join(self.folder, self.imgs_paths.next())
		self.loadImage(path)
		

	def previousImage(self):
		path = os.path.join(self.folder, self.imgs_paths.prev())
		self.loadImage(path)


	def loadImage(self, path):
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


	def label(self, event):
		string_repr = repr(event.char)
		if (string_repr == '\' \''):
			print("tried to open image")
			self.nextImage()
		elif (string_repr == '\'b\''):
			self.previousImage()
