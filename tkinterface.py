import tkinter as tk
import time
import math
import copy
from PIL import ImageTk, Image
from gamelogic import GameLogic
from tile import Tile


NUMBERS  = 1



class App(object):
    def __init__(self, master, **kwargs):
        self.master = master
        self.type = NUMBERS
        self.w = 500
        self.canvas = tk.Canvas(self.master, width=self.w, height=self.w)
        self.canvas.pack()
        self.n = 4
        self.model = GameLogic(self.n)
        self.size = self.w // self.n
        self.seed = []
        self.gameOver = False
        self.textures = self.loadTextures()
        self.bind()  # bind mouse and keys to the tkinter
        self.master.after(0, self.draw)
        self.onShuflle = True
        self.shuffleBoard()

    def loadTextures(self):
        if self.type == NUMBERS:
            im = Image.open("textures/wood.jpg")
            im = im.resize(
                (self.size-2, self.size-2))
            ph = ImageTk.PhotoImage(im)
            return ph

    def bind(self):
        self.master.bind("<Right>", self.arrowKey)
        self.master.bind("<Left>", self.arrowKey)
        self.master.bind("<Up>", self.arrowKey)
        self.master.bind("<Down>", self.arrowKey)
        self.master.bind("<Key>", self.key)
        self.canvas.bind("<Button-1>", self.mouse)

    def shuffleBoard(self):
        self.seed = self.model.getSeed()
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
        # transposing when getting point
        y, x = self.getPos(event.x), self.getPos(event.y)
        if not self.onShuflle and  (x, y != self.model.empty):
            self.model.moveByBlock(x, y)
            self.master.after(0, self.draw)

    def getTiles(self, n):
        board = self.model.getBoard()
        # tiles = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        tiles = copy.deepcopy(board)
        # tiles1 = [[0]*self.n] * self.n

        for i in range(len(board)):
            for j in range(len(board[i])):
                newTile = Tile(
                    self.canvas, board[i][j], self.type, j*self.size, i*self.size, self.size, self.textures)
                tiles[i][j] = newTile
        return tiles

    def drawTiles(self):
        self.canvas.delete("all")
        for row in self.tiles:
            for tile in row:
                tile.display()




root = tk.Tk()
app = App(root)
root.mainloop()
