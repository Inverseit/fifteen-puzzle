# Provides the main offline game
# import python libs
import tkinter as tk
from tkinter import messagebox
import tkinter.filedialog
import time
import math
import random
import copy
import os
from PIL import ImageTk, Image, ImageEnhance

# import my classes
from gamelogic import GameLogic
from timer import Timer
from solve import Solver
from tile import Tile
from icons import Icon

# game constant
NUMBERS = 1

class App(object):
    # Implements the app class, the GUI
    def __init__(self, master, **kwargs):
        self.master = master
        self.type = NUMBERS
        self.n = 4
        self.w = 500
        self.h = self.w+100
        self.imagePath = "textures/tartan.jpg"
        # app state
        self.started = False
        self.onPauseMenu = False
        self.onMenu = True
        self.icons = {}
        # setup canvas
        self.canvas = tk.Canvas(self.master, width=self.w, height=self.h)
        self.canvas.pack()
        # bind mouse and keys to the tkinter
        self.bind()
        self.loadSources()
        # main menu
        self.setUpMenu()
        self.showMenu()

    def loadSources(self):
        # loads images and sets on the class variables
        self.openImages()
        self.setIcons()

    def startGame(self):
        # starts game
        # change app state
        self.started = True
        self.gameOver = False
        self.robotSolved = False
        self.model = GameLogic(self.n)
        self.seed = []
        self.numberOfMoves = 0
        self.t = Timer(self.master, self.canvas)
        # run draw loop
        self.master.after(0, self.draw)
        # start shuffling the board
        self.shuffleBoard()

    def shuffleBoard(self):
        # prepares state of game and draws shuffle animation
        self.onPause = True
        self.seed = self.model.getShuffleSeed()
        self.shuffleAnimaion(self.seed)

    def shuffleAnimaion(self, seed):
        # draws shuffle animation
        self.draw()
        if not seed:
            self.onPause = False
            return
        self.model.moveDirection(seed[0])
        seed = seed[1:]
        self.master.after(50, lambda seed=seed: self.shuffleAnimaion(seed))

    def openImages(self):
        # opens icons and images and saves as variables in the app
        im = Image.open("textures/bg/"+"gyr.jpg")
        self.bg = ImageTk.PhotoImage(im)
        # TO BE CHANGEEEEEEEED
        bgButton = Image.open("textures/bg/button.png").convert("RGBA")
        self.bgButtonTrans = ImageTk.PhotoImage(self.reduce_opacity(bgButton, 0.95))
        self.bgButton = ImageTk.PhotoImage(bgButton)
        self.run = {}
        run = Image.open("textures/icons/run.png").convert("RGBA")
        run = run.resize((320, 70), Image.ANTIALIAS)
        self.run["off"] = ImageTk.PhotoImage(self.reduce_opacity(run, 0.95))
        self.run["on"] = ImageTk.PhotoImage(run)

        bgPause = Image.open("textures/bg/15class.png").convert("RGBA")
        self.bgPause = ImageTk.PhotoImage(self.reduce_opacity(bgPause, 0.96))
        self.iconList = ["home", "pause", "restart", "bot", "play"]
        for iconName in self.iconList:
            icon = Image.open("textures/icons/"+iconName +
                              ".png").convert("RGBA")
            if iconName == "play":
                icon = icon.resize((120, 120), Image.ANTIALIAS)
            self.icons[iconName] = {}
            self.icons[iconName]["on"] = ImageTk.PhotoImage(icon)
            self.icons[iconName]["off"] = ImageTk.PhotoImage(
                self.reduce_opacity(icon, 0.5))
            self.icons[iconName]["state"] = False

    def setBG(self):
        # sets bg of the app
        self.canvas.create_image(0, 0, image=self.bg, anchor='nw')

    def setIcons(self):
        # Draw icons at the bottom of canvas
        begin = 40
        margin = 120
        height = 510
        self.icons["home"]["tag"] = self.canvas.create_image(
            begin, height, image=self.icons["home"]["off"], anchor="nw")
        self.icons["restart"]["tag"] = self.canvas.create_image(
            begin + margin, height, image=self.icons["restart"]["off"], anchor="nw")
        self.icons["pause"]["tag"] = self.canvas.create_image(
            begin + 2*margin, height, image=self.icons["pause"]["off"], anchor="nw")
        self.icons["bot"]["tag"] = self.canvas.create_image(
            begin+3*margin, height, image=self.icons["bot"]["off"], anchor="nw")
        self.icons["play"]["tag"] = 0

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
        # bonds input to the tkinter
        self.master.bind("<Right>", self.arrowKey)
        self.master.bind("<Left>", self.arrowKey)
        self.master.bind("<Up>", self.arrowKey)
        self.master.bind("<Down>", self.arrowKey)
        self.master.bind("<Key>", self.key)
        self.canvas.bind("<Button-1>", self.mouse)
        self.canvas.bind("<Motion>", self.moved)

    def handleGameOver(self):
        # in case game is over and user solved 
        if not self.robotSolved and self.gameOver:
            if tk.messagebox.askyesno(title="Congrats!!!", message="You solved the puzzle in " + str(self.t.getTotal()) + " seconds. Using " + str(self.numberOfMoves) + " moves. Do you want to play again?"):
                self.model.reInit()
                self.gameOver = False
                self.onPause = True
                # self.shuffleBoard()
                self.t.stop()
                self.t.delete()
                self.startGame()
                return

    def draw(self):
        # draws objects on the canvas
        if self.onMenu:
            return
        else:
            self.tiles = self.getTiles(self.n)
            self.drawTiles()
        if self.model.isGameOver() and not self.onPause:
            self.gameOver = True
            self.t.stop()
            self.handleGameOver()

#  Move input handlers

    def key(self, event):
        c = event.char.upper()
        if c in ["W", "A", "S", "D"]:
            dirs = {"A": "L", "S": "D", "W": "U", "D": "R"}
            if self.drawMoveDirection(dirs[c]):
                # run timer only after first move
                if self.numberOfMoves == 0:
                    self.t.run()
                self.numberOfMoves += 1
                if self.model.isGameOver() and not self.onPause:
                    self.gameOver = True
                    self.t.stop()

    def arrowKey(self, event):
        d = event.keysym[0]
        if d in ["U", "D", "L", "R"]:
            if self.drawMoveDirection(d):
                if self.numberOfMoves == 0:
                    print("run")
                    self.t.run()
                self.numberOfMoves += 1
                if self.model.isGameOver() and not self.onPause:
                    self.gameOver = True
                    self.t.stop()

    def getPos(self, x):
        pos = math.floor(x / self.size)
        if pos < 0:
            pos = 0
        if pos >= self.n:
            pos -= 1
        return pos

    def drawMoveDirection(self, direction):
        if self.onPause:
            return
        res = self.model.moveDirection(direction)
        self.master.after(0, self.draw)
        return res

    def mouse(self, event):
        # Mouse click handler general
        if self.onMenu:
            self.menuClick(event)
            return
        else:
            this = self.canvas.find_withtag(tk.CURRENT)
            foundButton = [name for name in self.iconList if self.icons[name]
                           ["tag"] == this[0]]
            if foundButton:
                self.iconClickHandle(foundButton[0])
                return
        # transposing when getting point

        y = self.getPos(event.x)
        x = self.getPos(event.y) if event.y < self.w else -1
        if x < 0:
            return
        if not self.onPause and not self.onPauseMenu and (x, y != self.model.empty):
            if self.model.moveByBlock(x, y):
                if self.numberOfMoves == 0:
                    self.t.run()
                self.numberOfMoves += 1
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
        self.setIcons()
        for row in self.tiles:
            for tile in row:
                tile.display()

    def moved(self, event):
        # Event hover handler on mouse move
        if self.onMenu:
            return
        this = self.canvas.find_withtag(tk.CURRENT)
        if this:
            found = [name for name in self.iconList if self.icons[name]
                     ["tag"] == this[0]]
            if found:
                name = found[0]
                self.icons[name]["state"] = True
                self.canvas.itemconfig(
                    self.icons[name]["tag"], image=self.icons[name]["on"])
            else:
                for name in self.iconList:
                    if self.icons[name]["state"]:
                        self.canvas.itemconfig(
                            self.icons[name]["tag"], image=self.icons[name]["off"])
            # add here main menu icon handler

    def iconClickHandle(self, name):
        # down menu handlers
        if name == "restart":
            self.model.reInit()
            self.gameOver = False
            self.onPause = True
            # self.shuffleBoard()
            self.t.stop()
            self.t.delete()
            self.startGame()
            return
        if name == "bot":
            self.robotSolved = True
            s = Solver(self.model, self.n)
            self.loading = True
            solution, time = s.getSolution()
            self.loading = False
            print(time)
            self.shuffleAnimaion(solution)
        if name == "home":
            self.onMenu = True
            self.showMenu()
            self.t.stop()
        if name == "pause":
            self.onPauseMenu = True
            self.showPause()
            self.t.stop()
        if name == "play":
            self.onPauseMenu = False
            self.t.resume()
            self.draw()
            # self.t.resume()


    def setUpMenu(self):
        # creates menu objects
        self.menu = {}
        self.mi = {}
        self.mi["3"] = Icon(3, "3on", offPath="3off", resize=(90, 90))
        self.mi["4"] = Icon(4, "4on", offPath="4off",
                            resize=(90, 90), state=True)
        self.mi["5"] = Icon(5, "5on", offPath="5off", resize=(90, 90))

        self.mi["C"] = Icon(1, "onC", offPath="offC",
                            resize=(130, 65), state=True)
        self.mi["I"] = Icon(2, "Ion", offPath="Ioff", resize=(130, 65))

    def showMenu(self):
        # displays menu
        self.setBG()
        x = 50
        y = 50
        s = 400
        self.canvas.create_text(
            250, y+40, text="Choose the size of the board", font="Helvetica 16")
        x = 50
        y = y+70
        size = 90
        padding = 50
        margin = (s - 3*size - 2*padding) // 2
        font = "Helvetica 40 bold"

        x0, y0 = x+padding, y
        cur = self.mi["3"]
        cur.setTag(self.canvas.create_image(
            x0, y0, image=cur.get(), anchor='nw'))

        x0, y0 = x+padding+margin+size, y
        cur = self.mi["4"]
        cur.setTag(self.canvas.create_image(
            x0, y0, image=cur.get(), anchor='nw'))

        x0, y0 = x+padding + 2*(margin+size), y
        cur = self.mi["5"]
        cur.setTag(self.canvas.create_image(
            x0, y0, image=cur.get(), anchor='nw'))

        y = y + size+padding
        self.canvas.create_text(
            250, y-20, text="Choose the regime of the game", font="Helvetica 16")

        size = 130
        margin = s - 2*size - 2*padding

        x0, y0 = x+padding, y
        cur = self.mi["C"]
        cur.setTag(self.canvas.create_image(
            x0, y0, image=cur.get(), anchor='nw'))
        x0, y0 = x+padding+margin+size, y
        cur = self.mi["I"]
        cur.setTag(self.canvas.create_image(
            x0, y0, image=cur.get(), anchor='nw'))
        self.menu["start"] = self.canvas.create_image(
            90, 370, image=self.run["on"], anchor='nw')

    def menuClick(self, event):
        # handle menu clicks using tags in canvas
        this = self.canvas.find_withtag(tk.CURRENT)
        if this:
            # handle number button clicks
            if this[0] == self.mi["3"].getTag():
                self.mi["3"].toggle()
                self.n = 3
            if this[0] == self.mi["4"].getTag():
                self.mi["4"].toggle()
                self.n = 4
            if this[0] == self.mi["5"].getTag():
                self.mi["5"].toggle()
                self.n = 5
            for i in ["3", "4", "5"]:
                if str(self.n) != i:
                    self.mi[i].turnOff()
            if this[0] == self.mi["C"].getTag():
                print("num")
                self.type = NUMBERS
                self.mi["I"].turnOff()
                self.mi["C"].turnOn()
            elif this[0] == self.mi["I"].getTag():
                if self.getImagePath():
                    self.type = NUMBERS+1
                    self.mi["I"].turnOn()
                    self.mi["C"].turnOff()
            elif this[0] == self.menu["start"]:
                print("starting")
                self.onMenu = False
                self.size = self.w // self.n
                self.textures = self.loadTextures(self.imagePath)
                self.startGame()
                return
            self.showMenu()

    def getImagePath(self):
        # promt image dialog
        f = tkinter.filedialog.askopenfilename(
            parent=self.master, initialdir='C:/Users/User/Desktop/FALL 2020/15112/fifteen-puzzle>',
            title='Choose file',
            filetypes=[('png images', '.png'),
                       ('gif images', '.gif'), ('jpg images', '.jpg')]
        )
        if f:
            self.imagePath = f
            print(self.imagePath)
            return True
        else:
            print("You didn't choose the image.")
            return False

    def showPause(self):
        # draws pause menu
        self.menu["bg"] = self.canvas.create_image(
            0, 0, image=self.bgPause, anchor='nw')
        self.icons["play"]["tag"] = self.canvas.create_image(
            195, 195, image=self.icons["play"]["off"], anchor="nw")

    # Image utils

    def crop(self, infile):
        # crops an image into n^2 parts and return array of images
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
                piece = im.crop(box)
                img = Image.new('RGB', (self.size, self.size), 255)
                img.paste(piece)
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

    # from https://stackoverflow.com/questions/44099594/how-to-make-a-tkinter-canvas-rectangle-with-rounded-corners
    def round_rect(self, x1, y1, x2, y2, fill="red", radius=25, **kw):
        # draws rounded rectangles
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
        return self.canvas.create_polygon(points, fill=fill, width=2, smooth=True, **kw)


if __name__ == "__main__":
    # application running
    root = tk.Tk()
    app = App(root)
    root.mainloop()
