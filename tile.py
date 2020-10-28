import tkinter as tk
from PIL import ImageTk, Image
NUMBERS  = 1

class Tile(object):
    def __init__(self, canvas, number, boardType, x, y, size, textures):
        self.size = size
        self.x = x
        self.y = y
        self.number = number
        self.canvas = canvas
        self.boardType = boardType
        self.textures = textures
        # self.img =

    def update(self, number):
        self.number = number
    # from https://stackoverflow.com/questions/44099594/how-to-make-a-tkinter-canvas-rectangle-with-rounded-corners

    def round_rect(self, x1, y1, x2, y2, radius=25):
        points = [x1+radius, y1,
                  x1+radius, y1,
                  x2-radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1+radius,
                  x1, y1]
        return self.canvas.create_polygon(points,outline='black', fill='', width = 2, smooth=True)

    def display(self):
        if self.boardType == NUMBERS:
            if self.number == 0:
                return
            size = self.size
            x, y = self.x, self.y
            number = self.number

            # im = Image.open("textures/wood.jpg")
            self.margin = 2
            # im = im.resize((self.size-self.margin, self.size-self.margin))
            # self.image = ImageTk.PhotoImage(im)
            # print(self.image)
            self.canvas.create_image(
                x+self.margin, y+self.margin, image=self.textures, anchor='nw')
            self.id = self.round_rect(
                x, y, x+size, y+size)
            self.label = self.canvas.create_text(x+size/2, y+size/2, text=number, font="Times 20 italic bold")
