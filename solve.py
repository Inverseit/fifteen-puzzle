import time
from queue import PriorityQueue
from copy import deepcopy

class Positions(object):
    def __init__(self, lvl, board, empty, path,n):
        self.n = n
        self.goal = self.getGoalBoard()
        self.goalString = self.getHashString(board = self.goal)
        self.level = lvl
        self.board = board
        self.empty = empty
        self.path = path
        self.getHashString(self.board)
        self.calculateCost()

    def getGoalBoard(self):
        board = []
        sz = self.n
        board = [[j for j in range(i*sz+1, (i+1)*sz+1)] for i in range(sz)]
        board[-1][-1] = 0  # make the last element 0 (empty)
        return board

    def calculateCost(self):
        self.cost = self.level + self.manhDist()
    
    def getCost(self):
        return self.cost

    def __lt__(self, other):
        # comparing operator
        return self.cost < other.getCost()

    def getInitBoard(self):
        board = []
        n = self.n
        board = [[j for j in range(i*n+1, (i+1)*n+1)] for i in range(n)]
        board[-1][-1] = 0  # make the last element 0 (empty)
        return board
    
    def getHashString(self, board):
        hashString = ""
        for i in range(self.n):
            for j in range(self.n):
                hashString += (str(board[i][j]) + ",")
        self.hashString = hashString
        return hashString 

    def isSolved(self):
        # print(self.hashString, self.goalString)
        return self.hashString == self.goalString

    def __hash__(self):
        return hash(self.hashString)

    def possibleMoves(self):
        # moves = [(-1, 0, "U"), (1, 0, "D"), (0, -1, "L"), (0, 1, "R")]
        vectors = {
            "U": (-1, 0), 
            "D": (1, 0),
            "L": (0, -1), 
            "R": (0, 1)}
        row, col = self.empty
        for move in vectors.keys():
            new = self.addTuples(self.empty, vectors[move])
            if 0 <= new[0] < self.n and 0 <= new[1] < self.n:
                tmp = deepcopy(self.board)
                tmp[row][col], tmp[new[0]][new[1]] =\
                                                 tmp[new[0]][new[1]], tmp[row][col]
                newEmpty = new
                yield tmp, newEmpty, move
        return

    def manhDist(self):
        dist = 0
        n = self.n
        for i in range(n):
            for j in range(n):
                num = self.board[i][j]
                if num != self.goal[i][j] and num != 0:
                    row, col = (num - 1) // n, (num - 1) % n
                    dist += abs(i - row) + abs(j - col)
        return dist


    @staticmethod
    def addTuples(t1, t2): # adds tuples componentwise
        return tuple(map(lambda i, j: i + j, t1, t2))


class Solver():
    def __init__(self, g, n):
        self.n = n
        self.start = time.time()
        self.g = g
        self.board = g.getBoard()
        self.empty = (n-1, n-1)
        self.queue = PriorityQueue()
        self.visited = set()

    def getSolution(self):
        return self.solve()
    
    def tMove(self,move):
        translation  = { "U": "D", "D": "U", "R": "L", "L": "R" }
        return translation[move]

    def solve(self):
        root = Positions(0, self.board, self.empty, "", self.n)
        self.queue.put(root)

        i = 0
        while not self.queue.empty():
            pos = self.queue.get()

            if i % 5000 == 0:
                print("checking " + str(i) + "th position, level is ",
                    str(pos.level), "cost is ", str(pos.cost))
            i += 1

            if pos.level > 70:
                solution = "No under 70"
                break

            if pos.isSolved():
                solution = pos.path
                break

            for newBoard, newEmpty, move in pos.possibleMoves():
                newPos = Positions(pos.level+1, newBoard,
                                   newEmpty, pos.path + self.tMove(move), self.n)
                if newPos not in self.visited:
                    self.visited.add(newPos)
                    self.queue.put(newPos)
        print(time.time() - self.start, solution)
        return solution


if __name__ == "__main__":
    g = GameLogic(4)
    g.shuffleBoard()
    print(g)
    soln = Solver(g, 4).getSolution()
    print(soln)
