import tkinter as tk
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


NUMBERS  = 1

class App(object):
    def __init__(self, master, **kwargs):
        self.master = master
        self.type = NUMBERS
        self.n = 4
        self.w = 500
        self.h = self.w+100
        self.size = self.w // self.n
        self.canvas = tk.Canvas(self.master, width=self.w, height=self.h)
        self.imagePath = "textures/tartan.jpg"
        # self.on = False
        self.canvas.bind("<Motion>", self.moved)
        self.canvas.pack()
        # self.setButton()
        
        self.loadSources()
        
        # bind mouse and keys to the tkinter
        self.bind()
        self.started = False
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
        self.t = Timer(self.master, self.canvas)        

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
        self.shuffleAnimaion(self.seed)

    def shuffleAnimaion(self, seed):
        self.draw()
        if not seed:
            self.onPause = False
            return
        self.model.moveDirection(seed[0])
        seed = seed[1:]
        self.master.after(50, lambda seed=seed:self.shuffleAnimaion(seed))

    def draw(self):
        if self.gameOver:
            print("no need to continue")
        elif self.onMenu:
            return
        else:
            self.tiles = self.getTiles(self.n)
            self.drawTiles()
            if self.model.isGameOver() and not self.onPause:
                # print("GAMEEEEEEEEEEEEE OVERRRRRRRRRRRRRRRRRRR")
                self.gameOver = True
                self.t.stop()
            # print(self.numberOfMoves)
    
    def key(self, event):
        c = event.char.upper()
        if c in ["W", "A", "S", "D"]:
            dirs = {"A": "L", "S": "D", "W":"U" ,"D":"R"}
            if self.drawMoveDirection(dirs[c]):
                # run timer only after first move
                if self.numberOfMoves == 0:
                    print("run")
                    self.t.run()
                self.numberOfMoves += 1

    def arrowKey(self, event):
        d = event.keysym[0]
        if d in ["U", "D", "L", "R"]:
            if self.drawMoveDirection(d):
                if self.numberOfMoves == 0:
                    print("run")
                    self.t.run()
                self.numberOfMoves += 1
    
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
            print("lol")
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
        if not self.onPause and  (x, y != self.model.empty):
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
            self.shuffleBoard()
            return
        if name == "bot":
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
            self.onPause = True
            self.t.stop()

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
        self.menu["3"] = {}
        self.menu["3"]["state"] = False
        self.menu["3"]["val"] = 3
        self.menu["4"] = {}
        self.menu["4"]["state"] = True
        self.menu["4"]["val"] = 4
        self.menu["5"] = {}
        self.menu["5"]["state"] = False
        self.menu["5"]["val"] = 5
        self.menu["num"] = {}
        self.menu["img"] = {}
        self.menu["num"]["state"] = True
        self.menu["img"]["state"] = False
 
    def showMenu(self):
        x = 50
        y = 50
        s = 400
        self.menu["bg"] = self.round_rect(x, y, x+s, y+s)
        self.canvas.create_text(250, y+40, text="Choose the size of the board", font="Helvetica 16")
        x = 50
        y = y+70
        size = 90
        padding = 50
        margin = (s - 3*size - 2*padding) // 2 
        font = "Helvetica 40 bold"
        
        x0, y0 = x+padding, y
        cur = self.menu["3"]
        cur["tags"] = {}
        cur["tags"]["bg"]  = self.round_rect(x0,y0 , x0+size, y0+size, fill="blue")
        cur["tags"]["txt"] = self.canvas.create_text(x0+ size//2, y0+size//2, text="3", font=font)

        if cur["state"]:
            self.canvas.itemconfig(cur["tags"]["bg"], outline = "black")
            self.canvas.itemconfig(cur["tags"]["txt"], fill = "gold")
        
        x0, y0 = x+padding+margin+size, y
        cur = self.menu["4"]
        cur["tags"] = {}
        cur["tags"]["bg"] = self.round_rect(
            x0, y0, x0+size, y0+size, fill="blue")
        cur["tags"]["txt"] = self.canvas.create_text(
            x0 + size//2, y0+size//2, text="4", font=font)

        if cur["state"]:
            self.canvas.itemconfig(cur["tags"]["bg"], outline="black")
            self.canvas.itemconfig(cur["tags"]["txt"], fill="gold")

        x0, y0 = x+padding + 2*(margin+size), y
        cur = self.menu["5"]
        cur["tags"] = {}
        cur["tags"]["bg"] = self.round_rect(
            x0, y0, x0+size, y0+size, fill="blue")
        cur["tags"]["txt"] = self.canvas.create_text(
            x0 + size//2, y0+size//2, text="5", font=font)

        if cur["state"]:
            # if this button activated change it's style
            self.canvas.itemconfig(cur["tags"]["bg"], outline="black")
            self.canvas.itemconfig(cur["tags"]["txt"], fill="gold")


        y = y +size+padding
        self.canvas.create_text(
            250, y-20, text="Choose the regime of the game", font="Helvetica 16")
        
        size = 130
        margin = s - 2*size - 2*padding

        x0, y0 = x+padding, y
        font = "Helvetica 16 bold"
        cur = self.menu["num"]
        cur["tags"] = {}
        cur["tags"]["bg"]  = self.round_rect(x0,y0 , x0+size, y0+size//2, fill="blue")
        cur["tags"]["txt"] = self.canvas.create_text(x0+ size//2, y0+size//4, text="Classic", font=font)
        
        if cur["state"]:
            self.canvas.itemconfig(cur["tags"]["bg"], outline="black")
            self.canvas.itemconfig(cur["tags"]["txt"], fill="gold")
        x0, y0 = x+padding+margin+size, y
        cur = self.menu["img"]
        cur["tags"] = {}
        cur["tags"]["bg"]  =  self.round_rect(x0,y0 , x0+size, y0+size//2, fill="blue")
        cur["tags"]["txt"] =  self.canvas.create_text(x0+ size//2, y0+size//4, text="Image", font=font, fill= "white")

        if cur["state"]:
            self.canvas.itemconfig(cur["tags"]["bg"], outline="black")
            self.canvas.itemconfig(cur["tags"]["txt"], fill="gold")
        
        self.menu["start"] = self.round_rect(90, 370, 410, 425, fill="green", outline = "black")

    def menuClick(self, event):
        print("here")
        this = self.canvas.find_withtag(tk.CURRENT)
        if this:
            # handle number button clicks
            if this[0] in self.menu["3"]["tags"].values():
                self.menu["3"]["state"] = True
                self.menu["4"]["state"] = False
                self.menu["5"]["state"] = False
                print("changed")
                self.n = self.menu["3"]["val"]
                print(self.n)
            if this[0] in self.menu["4"]["tags"].values():
                self.menu["4"]["state"] = True
                self.menu["3"]["state"] = False
                self.menu["5"]["state"] = False
                print("changed")
                self.n = self.menu["4"]["val"]
                print(self.n)
            if this[0] in self.menu["5"]["tags"].values():
                self.menu["5"]["state"] = True
                self.menu["4"]["state"] = False
                self.menu["3"]["state"] = False
                print("changed")
                self.n = self.menu["5"]["val"]
                print(self.n)
            # handle game type
            print("here")
            if this[0] in self.menu["num"]["tags"].values():
                print("num")
                self.type = NUMBERS
                self.menu["num"]["state"] = True
                self.menu["img"]["state"] = False
                print("changed to numbers")
                return
            if this[0] in self.menu["img"]["tags"].values():
                self.type = NUMBERS+1
                self.menu["num"]["state"] = False
                self.menu["img"]["state"] = True
                self.getImagePath()
                print("changed to imgs")
                return
            if this[0] == self.menu["start"]:
                print("starting")
                self.onMenu = False
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

root = tk.Tk()
app = App(root)
root.mainloop()
