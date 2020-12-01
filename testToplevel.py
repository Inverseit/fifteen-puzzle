
from tkinter import messagebox
import random
from icons import Icon
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


class App(tk.Toplevel):
    def __init__(self, master, seed, friend, comm):
        super().__init__(master)
        self.master = master
        self.type = 1
        self.n = 4
        self.w = 500
        self.h = self.w+100
        self.canvas = tk.Canvas(self, width=self.w, height=self.h)
        self.seed = seed
        self.comm = comm
        self.friend = friend
        self.canvas.pack()
        self.loadSources()
        self.f = False
        self.startGame()

    def loadSources(self):
        self.icons = {}
        self.textures  = self.loadTextures("")
        backgrounds = ["gyr.jpg", "gyr.jpg"]
        bgPath = random.choice(backgrounds)
        im = Image.open("textures/bg/"+bgPath)
        self.bg = ImageTk.PhotoImage(im)

    def startGame(self):
        self.started = True
        self.model = GameLogic(self.n)
        self.gameOver = False
        self.onPause = True
        self.master.after(0, self.draw)
        self.numberOfMoves = 0
        self.shuffleBoard()
        self.canvas.bind("<Button-1>", self.mouse)
        self.t = Timer(self.master, self.canvas)

    def setBG(self):
        self.canvas.create_image(0, 0, image=self.bg, anchor='nw')

    def crop(self, infile):
        im = Image.open(infile)
        width, height = im.size
        imgwidth = self.w
        imgheight = imgwidth * height // width
        im = im.resize((imgwidth, imgheight), Image.ANTIALIAS)
        cropped = []
        for i in range(self.n):
            for j in range(self.n):
                box = (j*125, i*125, (j+1)
                       * 125, (i+1)*125)
                piece = im.crop(box)
                img = Image.new('RGB', (125, 125), 255)
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
        infile = "textures/wood.jpg"
        alpha = int(0.5 * 255)
        fill = "#0269A4"
        fill = self.master.winfo_rgb(fill) + (alpha,)
        im = Image.new('RGBA', (123, 123), fill)
        # im = im.putalpha(128)
        ph = ImageTk.PhotoImage(im)
        number = self.n * self.n
        return [ph] * number


    def shuffleBoard(self):
        # self.seed = self.model.getShuffleSeed()
        self.shuffleAnimaion(self.seed)

    def shuffleAnimaion(self, seed):
        self.draw()
        if not seed:
            self.onPause = False
            return
        self.model.moveDirection(seed[0])
        seed = seed[1:]
        self.master.after(50, lambda seed=seed: self.shuffleAnimaion(seed))

    def handleGameOver(self):
        # actions when game is over
        if self.gameOver:
            self.timeFinished = round(self.t.getTotal(), 2)
            self.comm.sendMessage(self.friend, "W"+str(self.timeFinished))
            self.done()  # should be you won or sth
            tk.messagebox.showinfo(message="CONGRATSSSSSSS")
            self.destroy()

    def draw(self):
        self.tiles = self.getTiles(self.n)
        self.drawTiles()
        self.putNumberOfMoves()
        if self.model.isGameOver() and not self.onPause:
            self.gameOver = True
            self.t.stop()
            self.handleGameOver()

    def getPos(self, x):
        pos = math.floor(x / 125)
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

    def putNumberOfMoves(self):
        # puts number of moves into the screen
        self.canvas.create_text(
            100, 520, text="Your #moves:" + str(self.numberOfMoves), font="Helvetica 16")
        self.canvas.create_text(
            100, 540, text="Opponent #moves:", font="Helvetica 16")

    def setFriendStat(self, s):
        # get's number of moves from friend
        if self.f:
            try:
                self.canvas.delete(self.f)
            except Exception:
                pass
        self.f = self.canvas.create_text(200, 540, text=s, font="Helvetica 16")

    def mouse(self, event):
        # handles mouse input
        y = self.getPos(event.x)
        x = self.getPos(event.y) if event.y < self.w else -1
        if x < 0:
            return
        if not self.onPause and (x, y != self.model.empty):
            if self.model.moveByBlock(x, y):
                if self.numberOfMoves == 0:
                    self.t.run()
                self.numberOfMoves += 1
                self.putNumberOfMoves()
            self.master.after(0, self.draw)

    def getTiles(self, n):
        # returns tiles as a class objects
        board = self.model.getBoard()
        tiles = copy.deepcopy(board)    # copying to have exact same dimensions

        for i in range(len(board)):
            for j in range(len(board[i])):
                newTile = Tile(
                    self.canvas, board[i][j], self.type, j*125, i*125, 125, self.textures)
                tiles[i][j] = newTile
        return tiles

    def drawTiles(self):
        # draws tiles on the screen
        self.canvas.delete("all")
        for row in self.tiles:
            for tile in row:
                tile.display()

    def getMoves(self):
        # returns number of moves
        return self.numberOfMoves

    def getCanvas(self):
        # return canvas object
        return self.canvas


if __name__ == "__main__":
    root = tk.Tk()
    seed = "DDLLRDURLUDDURLDURL"
    friend = "User"
    comm = ""
    app = App(root, seed, friend, comm)
    root.mainloop()
