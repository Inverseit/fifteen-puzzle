import random
from pynput import keyboard
import os
class GameLogic():
    def __init__(self, n):
        self.n = n
        self.board = self.getInitBoard()
        self.goal = self.getInitBoard()
        self.empty = (self.n-1, self.n-1)

    def isGameOver(self):
        return self.board == self.goal

    def __repr__(self):
        out = ""
        for i in self.board:
            for j in i:
                l = len(str(j))
                if j == 0:
                    p = "__"
                else:
                    p = " " + str(j) if l == 1 else str(j)
                out += p + " "
            out += "\n"
        print(out, end="\r")
        return ""

    def getInitBoard(self):
        board = []
        sz = self.n
        board = [[j for j in range(i*sz+1, (i+1)*sz+1)] for i in range(sz)]
        board[-1][-1] = 0  # make the last element 0 (empty)
        return board
    
    def getBoard(self):
        return self.board

    def shuffleBoard(self):
        # board = self.board
        l = 20
        moves = ["U", "R", "L", "D"]
        cur = random.randint(0, 3)
        for i in range(l):
            if i != 1:
                prev = cur
                cur = random.randint(0, 3)
                # if sum is three is opposite moves, so no point doing it
                while cur + prev == 3:
                    cur = random.randint(0, 3)
            self.moveDirection(moves[cur])
        # do strict move to make empty on right bottom corner
        for _ in range(3):
            self.moveDirection("U")
        for _ in range(3):
            self.moveDirection("L")

    def getShuffleSeed(self):
        l = 50
        seed = []
        moves = ["U", "R", "L", "D"]
        cur = random.randint(0, 3)
        for i in range(l):
            if i != 1:
                prev = cur
                cur = random.randint(0, 3)
                # if sum is three is opposite moves, so no point doing it
                while cur + prev == 3:
                    cur = random.randint(0, 3)
            seed += [moves[cur]]
        # do strict move to make empty on right bottom corner
        for _ in range(3):
            seed += ["U"]
        for _ in range(3):
            seed += ["L"]
        return seed
    
    # make move by some direction
    def moveDirection(self, direction):
        vector = {"U": (1, 0), "D": (-1, 0), 
                  "L": (0, 1), "R": (0,-1)}
        new = self.addTuples(self.empty, vector[direction])
        if 0 <= new[0] < self.n and 0 <= new[1] < self.n:
            self.swap(*self.empty, *new)
            return True
        return False
    
    def reInit(self):
        self.board = self.getInitBoard()
        self.empty = (self.n-1, self.n-1)

    def moveByBlock(self,x, y):
        if (x > 0 and self.empty == (x - 1,y)):
            self.swap(x - 1, y, x, y)
            return True
        elif (y < self.n-1 and self.empty == (x,y + 1)):
            self.swap(x, y + 1, x, y)
            return True
        elif (x < self.n-1 and self.empty == (x + 1,y)):
            self.swap(x + 1, y, x, y)
            return True
        elif (y > 0 and self.empty == (x, y - 1)):
            self.swap(x, y - 1, x, y)
            return True
        else:
            return False
    # Swaps the value of two cells
    def swap(self, x1, y1, x2, y2):
        self.board[x1][y1] = self.board[x2][y2]
        self.board[x2][y2] = 0
        self.empty = (x2,y2)
    
    @staticmethod
    def addTuples(t1, t2):
        # adds tuples componentwise
        return tuple(map(lambda i, j: i + j, t1, t2))

if __name__ == "__main__":
    a = GameLogic(4)
    a.shuffleBoard()
    print(a)
    # a.startListening()
    # print(a)
