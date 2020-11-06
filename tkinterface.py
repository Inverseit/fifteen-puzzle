import tkinter as tk
import time
import math
import copy
import os
from PIL import ImageTk, Image, ImageEnhance
from gamelogic import GameLogic
from tile import Tile


NUMBERS  = 1



class App(object):
    def __init__(self, master, **kwargs):
        self.master = master
        self.type = NUMBERS
        self.w = 500
        self.h =  self.w+100
        self.canvas = tk.Canvas(self.master, width=self.w, height=self.h)
        self.icons = {}
        self.openImages()
        self.setImages()
        self.on = False
        self.canvas.bind("<Motion>", self.moved)
        self.canvas.pack()
        # self.setButton()
        self.n = 3
        self.model = GameLogic(self.n)
        self.size = self.w // self.n
        self.seed = []
        self.gameOver = False
        self.textures = self.loadTextures("textures/tartan.jpg")
        self.bind()  # bind mouse and keys to the tkinter
        self.master.after(0, self.draw)
        self.onShuflle = True
        self.shuffleBoard()

    def openImages(self):
        im = Image.open("textures/bg/gyr.jpg")
        self.bg = ImageTk.PhotoImage(im)
        self.iconList = ["home", "pause", "restart", "bot"]
        for iconName in self.iconList:
            icon = Image.open("textures/icons/"+iconName+".png").convert("RGBA")
            self.icons[iconName] = {}
            self.icons[iconName]["on"] = ImageTk.PhotoImage(icon)
            self.icons[iconName]["off"] = ImageTk.PhotoImage(
                self.reduce_opacity(icon, 0.5))
            self.icons[iconName]["state"] = False
        # bot = Image.open("textures/icons/bot2.png")
        # self.icons["bot"]["on"] = ImageTk.PhotoImage(bot)
        # pause = Image.open("textures/icons/pause.png")
        # self.icons["pause"]["on"] = ImageTk.PhotoImage(pause)
        # play = Image.open("textures/icons/play.png")
        # self.icons["play"]["on"] = ImageTk.PhotoImage(play)
        # restart = Image.open("textures/icons/restart.png")
        # self.icons["restart"]["on"] = ImageTk.PhotoImage(restart)

    def setBG(self):
        self.canvas.create_image(0, 0, image=self.bg, anchor='nw')

    def setImages(self):
        begin = 40
        margin = 120
        height = 510
        self.icons["home"]["tag"] = self.canvas.create_image(begin, height, image=self.icons["home"]["off"], anchor = "nw")
        self.icons["restart"]["tag"] = self.canvas.create_image(
            begin + margin, height, image=self.icons["restart"]["off"], anchor="nw")
        self.icons["pause"]["tag"] = self.canvas.create_image(
            begin + 2*margin, height, image=self.icons["pause"]["off"], anchor="nw")
        self.icons["bot"]["tag"] = self.canvas.create_image(
            begin+3*margin, height, image=self.icons["bot"]["off"], anchor="nw")



    def crop(self, infile):
        im = Image.open(infile)
        width, height = im.size
        imgwidth = self.w
        imgheight = imgwidth * height // width
        im = im.resize((imgwidth, imgheight), Image.ANTIALIAS)
        cropped = []
        for i in range(self.n):
            for j in range(self.n):
                box = (j*self.size, i*self.size, (j+1)
                       * self.size, (i+1)*self.size)
                piece =  im.crop(box)
                img = Image.new('RGB', (self.size, self.size), 255)
                img.paste(piece)
                # path = os.path.join('tmp/IMG-%s.jpg' % k)
                # k += 1
                # img.save(path)
                cropped.append(img)
        return cropped


    @staticmethod
    def reduce_opacity(im, opacity):
        """Returns an image with reduced opacity."""
        # from https://stackoverflow.com/questions/61271072/how-can-i-solve-python-3-pil-putalpha-problem
        assert opacity >= 0 and opacity <= 1
        if im.mode != 'RGBA':
            im = im.convert('RGBA')
        else:
            im = im.copy()
        alpha = im.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        im.putalpha(alpha)
        return im


    def loadTextures(self, infile):
        if self.type == NUMBERS:
            # im = Image.open("textures/gray.jpg")
            alpha = int(0.5 * 255)
            fill = "#BBBCB6"
            fill = self.master.winfo_rgb(fill) + (alpha,)
            im = Image.new('RGBA', (self.size-2, self.size-2), fill)
            # im = im.putalpha(128)
            ph = ImageTk.PhotoImage(im)
            number = self.n * self.n
            return [ph] * number
        else:
            textures = [0]
            pieces = self.crop(infile)
            for i in range(1, self.n*self.n):
                im = pieces[i-1]
                im = im.resize(
                    (self.size-2, self.size-2))
                ph = ImageTk.PhotoImage(im)
                textures.append(ph)
            return textures

    def bind(self):
        self.master.bind("<Right>", self.arrowKey)
        self.master.bind("<Left>", self.arrowKey)
        self.master.bind("<Up>", self.arrowKey)
        self.master.bind("<Down>", self.arrowKey)
        self.master.bind("<Key>", self.key)
        self.canvas.bind("<Button-1>", self.mouse)

    def shuffleBoard(self):
        self.seed = self.model.getShuffleSeed()
        self.shuffleAnimaion()

    def shuffleAnimaion(self):
        self.draw()
        if not self.seed:
            self.onShuflle = False
            return
        self.model.moveDirection(self.seed[0])
        self.seed = self.seed[1:]
        self.master.after(10, self.shuffleAnimaion)

    def draw(self):
        if self.gameOver:
            print("no need to continue")
        else:
            self.tiles = self.getTiles(self.n)
            self.drawTiles()
            if self.model.isGameOver() and not self.onShuflle:
                print("GAMEEEEEEEEEEEEE OVERRRRRRRRRRRRRRRRRRR")
                self.gameOver = True
    
    def key(self, event):
        c = event.char.upper()
        if c in ["W", "A", "S", "D"]:
            dirs = {"A": "L", "S": "D", "W":"U" ,"D":"R"}
            self.drawMoveDirection(dirs[c])

    def arrowKey(self, event):
        d = event.keysym[0]
        if d in ["U", "D", "L", "R"]:
            self.drawMoveDirection(d)
    
    def getPos(self, x):
        pos = math.floor(x / self.size)
        if pos < 0:
            pos = 0
        if pos >= self.n:
            pos -= 1
        return pos
        
    def drawMoveDirection(self, direction):
        if self.onShuflle:
            return
        self.model.moveDirection(direction)
        self.master.after(0, self.draw)

    def mouse(self, event):
        this = self.canvas.find_withtag(tk.CURRENT)
        foundButton = [name for name in self.iconList if self.icons[name]
                 ["tag"] == this[0]]
        if foundButton:
            self.buttonClick(foundButton[0])
            return
        # transposing when getting point
        y = self.getPos(event.x)
        x = self.getPos(event.y) if event.y < self.w else -1
        if x < 0:
            return
        if not self.onShuflle and  (x, y != self.model.empty):
            self.model.moveByBlock(x, y)
            self.master.after(0, self.draw)


    def getTiles(self, n):
        board = self.model.getBoard()
        tiles = copy.deepcopy(board)    # copying to have exact same dimensions

        for i in range(len(board)):
            for j in range(len(board[i])):
                newTile = Tile(
                    self.canvas, board[i][j], self.type, j*self.size, i*self.size, self.size, self.textures)
                tiles[i][j] = newTile
        return tiles


    def drawTiles(self):
        self.canvas.delete("all")
        self.setBG()
        self.setImages()
        for row in self.tiles:
            for tile in row:
                tile.display()

    def moved(self,event):
        this = self.canvas.find_withtag(tk.CURRENT)
        found = [name for name in self.iconList if self.icons[name]["tag"] == this[0]]
        if found:
            name = found[0]
            self.icons[name]["state"] = True
            self.canvas.itemconfig(
                self.icons[name]["tag"], image=self.icons[name]["on"])
        else:
            for name in self.iconList:
                if self.icons[name]["state"]:
                    self.canvas.itemconfig(self.icons[name]["tag"], image=self.icons[name]["off"])
                    self.on = False

    def buttonClick(self, name):
        print(name)

root = tk.Tk()
app = App(root)
root.mainloop()
