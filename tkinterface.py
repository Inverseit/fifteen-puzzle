import tkinter as tk
from tkinter import messagebox
import tkinter.filedialog
import time
import math
import copy
import os
from PIL import ImageTk, Image, ImageEnhance
from gamelogic import GameLogic
from timer import Timer
from solve import Solver
from tile import Tile

from icons import Icon

NUMBERS  = 1

class App(object):
    def __init__(self, master, **kwargs):
        self.master = master
        self.type = NUMBERS
        self.n = 4
        self.w = 500
        self.h = self.w+100
        self.canvas = tk.Canvas(self.master, width=self.w, height=self.h)
        self.loadSources()
        self.imagePath = "textures/tartan.jpg"
        # self.on = False
        self.canvas.bind("<Motion>", self.moved)
        self.canvas.pack()
        # self.setButton()
        
        
        # bind mouse and keys to the tkinter
        self.bind()
        self.started = False
        self.onPauseMenu = False
        self.onMenu = True
        self.setUpMenu()
        self.showMenu()
    
    def loadSources(self):
        self.icons = {}
        self.openImages()
        self.setImages()

    def startGame(self):
        self.started = True
        self.model = GameLogic(self.n)
        self.seed = []
        self.gameOver = False
        self.master.after(0, self.draw)
        self.numberOfMoves = 0
        self.onPause = True
        self.shuffleBoard()
        self.robotSolved = False
        self.t = Timer(self.master, self.canvas)

    def openImages(self):
        im = Image.open("textures/bg/gyr.jpg")
        self.bg = ImageTk.PhotoImage(im)
        # TO BE CHANGEEEEEEEED
        bgButton = Image.open("textures/bg/button.png").convert("RGBA")
        self.bgButtonTrans = ImageTk.PhotoImage(self.reduce_opacity(bgButton, 0.95))
        self.bgButton = ImageTk.PhotoImage(bgButton)

        self.run = {}
        run = Image.open("textures/icons/run.png").convert("RGBA")
        run = run.resize((320,70), Image.ANTIALIAS)
        self.run["off"] = ImageTk.PhotoImage(self.reduce_opacity(run, 0.95))
        self.run["on"] = ImageTk.PhotoImage(run)

        bgPause = Image.open("textures/bg/pause.png").convert("RGBA")
        self.bgPause = ImageTk.PhotoImage(self.reduce_opacity(bgPause, 0.96))
        self.iconList = ["home", "pause", "restart", "bot", "play"]
        for iconName in self.iconList:
            icon = Image.open("textures/icons/"+iconName+".png").convert("RGBA")
            if iconName == "play":
                icon = icon.resize((120, 120), Image.ANTIALIAS)
            self.icons[iconName] = {}
            self.icons[iconName]["on"] = ImageTk.PhotoImage(icon)
            self.icons[iconName]["off"] = ImageTk.PhotoImage(
                self.reduce_opacity(icon, 0.5))
            self.icons[iconName]["state"] = False
        # separate play from the basic list
        # self.iconList = self.iconList[:-1]

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
        self.icons["play"]["tag"] = 0 



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
        self.shuffleAnimaion(self.seed)

    def shuffleAnimaion(self, seed):
        self.draw()
        if not seed:
            self.onPause = False
            return
        self.model.moveDirection(seed[0])
        seed = seed[1:]
        self.master.after(50, lambda seed=seed:self.shuffleAnimaion(seed))

    def handleGameOver(self):
        if not self.robotSolved and self.gameOver:
            if tk.messagebox.askyesno(title = "Congrats!!!",message="You solved the puzzle in " + str(self.t.getTotal()) + " seconds. Using " + str(self.numberOfMoves) +" moves. Do you want to play again?"):
                self.model.reInit()
                self.gameOver = False
                self.onPause = True
                # self.shuffleBoard()
                self.t.stop()
                self.t.delete()
                self.startGame()
                return

    def draw(self):
        if self.gameOver:
            self.handleGameOver()
        elif self.onMenu:
            return
        else:
            self.tiles = self.getTiles(self.n)
            self.drawTiles()
        if self.model.isGameOver() and not self.onPause:
            self.gameOver = True
            self.t.stop()
            self.handleGameOver()
    
    def key(self, event):
        c = event.char.upper()
        if c in ["W", "A", "S", "D"]:
            dirs = {"A": "L", "S": "D", "W":"U" ,"D":"R"}
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
                self.buttonClick(foundButton[0])
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
        self.setImages()
        for row in self.tiles:
            for tile in row:
                tile.display()

    def moved(self,event):
        # Event hover handler on mouse move
        if self.onMenu:
            return
        this = self.canvas.find_withtag(tk.CURRENT)
        if this:
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
            # add here main menu icon handler

    def buttonClick(self, name):
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
        if name == "pause":
            self.onPauseMenu = True
            self.showPause()
            self.t.stop()
        if name == "play":
            self.onPauseMenu = False
            self.t.resume()
            self.draw()
            self.t.resume()
            

    # from https://stackoverflow.com/questions/44099594/how-to-make-a-tkinter-canvas-rectangle-with-rounded-corners
    def round_rect(self, x1, y1, x2, y2, fill = "red", radius=25, **kw):
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

    def setUpMenu(self):
        self.menu = {}
        # self.menu["3"] = {}
        # self.menu["3"]["state"] = False
        # self.menu["3"]["val"] = 3
        # self.menu["4"] = {}
        # self.menu["4"]["state"] = True
        # self.menu["4"]["val"] = 4
        # self.menu["5"] = {}
        # self.menu["5"]["state"] = False
        # self.menu["5"]["val"] = 5
        self.menu["num"] = {}
        self.menu["img"] = {}
        self.menu["num"]["state"] = True
        self.menu["img"]["state"] = False

        self.mi = {}
        self.mi["3"] = Icon(3,"3on", offPath="3off", resize=(90,90), state = True)
        self.mi["4"] = Icon(4,"4on", offPath="4off", resize=(90,90))
        self.mi["5"] = Icon(5, "5on", offPath="5off", resize=(90,90))

        self.mi["C"] = Icon(1, "onC", offPath="offC", resize=(130, 65), state = True)
        self.mi["I"] = Icon(2, "Ion", offPath="Ioff", resize=(130, 65))
 
    def showMenu(self):
        self.setBG()
        x = 50
        y = 50
        s = 400
        # self.menu["bg"] = self.round_rect(x, y, x+s, y+s)
        self.canvas.create_text(250, y+40, text="Choose the size of the board", font="Helvetica 16")
        x = 50
        y = y+70
        size = 90
        padding = 50
        margin = (s - 3*size - 2*padding) // 2 
        font = "Helvetica 40 bold"


        x0, y0 = x+padding, y
        cur = self.mi["3"]
        cur.setTag(self.canvas.create_image(x0, y0, image=cur.get(), anchor='nw'))
        
        x0, y0 = x+padding+margin+size, y
        cur = self.mi["4"]
        cur.setTag(self.canvas.create_image(x0, y0, image=cur.get(), anchor='nw'))

        x0, y0 = x+padding + 2*(margin+size), y
        cur = self.mi["5"]
        cur.setTag(self.canvas.create_image(x0, y0, image=cur.get(), anchor='nw'))


        y = y +size+padding
        self.canvas.create_text(250, y-20, text="Choose the regime of the game", font="Helvetica 16")
        
        size = 130
        margin = s - 2*size - 2*padding

        x0, y0 = x+padding, y
        # font = "Helvetica 16 bold"
        cur = self.mi["C"]
        cur.setTag(self.canvas.create_image(x0, y0, image=cur.get(), anchor='nw'))
        # cur["tags"] = {}

        # cur["tags"]["bg"]  = self.round_rect(x0,y0 , x0+size, y0+size//2, fill="blue")
        # cur["tags"]["txt"] = self.canvas.create_text(x0+ size//2, y0+size//4, text="Classic", font=font)
        
        # if cur["state"]:
        #     self.canvas.itemconfig(cur["tags"]["bg"], outline="black")
        #     self.canvas.itemconfig(cur["tags"]["txt"], fill="gold")
        x0, y0 = x+padding+margin+size, y
        cur = self.mi["I"]
        cur.setTag(self.canvas.create_image(
            x0, y0, image=cur.get(), anchor='nw'))
        # cur["tags"] = {}
        # cur["tags"]["bg"]  =  self.round_rect(x0,y0 , x0+size, y0+size//2, fill="blue")
        # cur["tags"]["txt"] =  self.canvas.create_text(x0+ size//2, y0+size//4, text="Image", font=font, fill= "white")

        # if cur["state"]:
        #     self.canvas.itemconfig(cur["tags"]["bg"], outline="black")
        #     self.canvas.itemconfig(cur["tags"]["txt"], fill="gold")
        
        # self.menu["start"] = self.round_rect(90, 370, 410, 425, fill="green", outline = "black")
        self.menu["start"] = self.canvas.create_image(90, 370, image=self.run["on"], anchor='nw')

    def menuClick(self, event):
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
                self.mi["I"].toggle()
                self.mi["C"].toggle()
            elif this[0] == self.mi["I"].getTag():
                self.type = NUMBERS+1
                self.mi["I"].toggle()
                self.mi["C"].toggle()
                self.getImagePath()
            elif this[0] == self.menu["start"]:
                print("starting")
                self.onMenu = False
                self.size = self.w // self.n
                self.textures = self.loadTextures(self.imagePath)
                self.startGame()
                return
            self.showMenu()

    def getImagePath(self):
        f = tkinter.filedialog.askopenfilename(
            parent=self.master, initialdir='C:/Users/User/Desktop/FALL 2020/15112/fifteen-puzzle>',
            title='Choose file',
            filetypes=[('png images', '.png'),
                    ('gif images', '.gif')]
        )
        if f:
            self.imagePath = f
            print(self.imagePath)
        else:
            print("You didn't choose the image.")

    def showPause(self):
        x = 100
        y = 100
        s = 400

        self.menu["bg"] = self.canvas.create_image(
            x, y, image=self.bgPause, anchor='nw')
        
        
        self.icons["play"]["tag"] = self.canvas.create_image( x+95, y+95, image=self.icons["play"]["off"], anchor="nw")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

