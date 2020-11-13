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

    def display(self):
        if True:
            if self.number == 0:
                return
            size = self.size
            x, y = self.x, self.y
            number = self.number

            # im = Image.open("textures/wood.jpg")
            self.margin = 3
            # im = im.resize((self.size-self.margin, self.size-self.margin))
            # self.image = ImageTk.PhotoImage(im)
            # print(self.image)
            self.canvas.create_image(
                x+self.margin, y+self.margin, image=self.textures[number], anchor='nw')
            if self.boardType == NUMBERS:
                # self.id = self.round_rect(x+self.margin, y+self.margin, x+size-self.margin, y+size-self.margin)
                self.label = self.canvas.create_text(x+size/2, y+size/2, text=number, font="Helvetica 50 bold")
