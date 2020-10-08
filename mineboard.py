from random import sample


class Mineboard:
    def populateGrid(self):
        """creates a 2d array containing all the game info"""
        true_grid = [[' ' for _ in range(self.width)]
                     for _ in range(self.height)]
        """initialises mines"""
        mine_places = sample(range(self.width * self.height), self.minecount)
        mine_places = [[num // self.width, num % self.width]
                       for num in mine_places]
        for loc in mine_places:
            i, j = loc[0], loc[1]
            true_grid[i][j] = 'M'
        """initialises the adjacency numbers"""
        for i in range(self.height):
            for j in range(self.width):
                if true_grid[i][j] == 'M':
                    continue
                nbrs = self.get_neighbours(i, j)
                nbr_mines = 0
                for nbr in nbrs:
                    if true_grid[nbr[0]][nbr[1]] == 'M':
                        nbr_mines += 1
                true_grid[i][j] = f"{nbr_mines}"
        return mine_places, true_grid

    def __init__(self, width, height, minecount):
        self.width = width
        self.height = height
        self.minecount = minecount
        self.mine_places, self.true_grid = self.populateGrid()
        self.gameboard = [
            [' ' for _ in range(self.width)] for _ in range(self.height)]
        self.gamestate = None  # keeps track of win/loss
        self.flagcount = 0  # keeps track of flags placed on board
        self.goodflags = 0  # keeps track of correctly placed flags
        self.revealed_count = 0  # keeps track of total revealed cells
        self.changes = []   # keeps track of changes made when updating board

    def check_win(self):
        """checks for game over"""
        all_seen = self.revealed_count == self.width * self.height - self.minecount
        if self.gamestate == 'lose':
            return 'lose'
        elif all_seen:
            return 'win'

    def get_neighbours(self, row, col):
        """returns all neighbours of a cell"""
        for i in range(max(0, row-1), min(self.height, row+2)):
            for j in range(max(0, col-1), min(self.width, col+2)):
                if (i, j) != (row, col):
                    yield [i, j]

    def reveal_cell(self, row, col):
        """deals with out of array guesses"""
        try:
            """Stops if already revealed"""
            if self.gameboard[row][col] != ' ':
                return
            self.gameboard[row][col] = self.true_grid[row][col]
            self.changes.append([row, col])
            self.revealed_count += 1
            """reveals all adjacent cells to a blank one"""
            if self.gameboard[row][col] == '0':
                nbrs = self.get_neighbours(row, col)
                for nbr in nbrs:
                    self.reveal_cell(nbr[0], nbr[1])
            if self.gameboard[row][col] == 'M':
                self.gamestate = 'lose'
            self.gamestate = self.check_win()
        except IndexError:
            return

    def flag_cell(self, row, col):
        """places a flag on a given cell"""
        try:
            self.changes.append([row, col])
            if self.gameboard[row][col] == ' ' and self.flagcount < self.minecount:
                self.gameboard[row][col] = 'F'
                self.flagcount += 1
                if self.true_grid[row][col] == 'M':
                    self.goodflags += 1
                self.gamestate = self.check_win()
            elif self.gameboard[row][col] == 'F':
                self.gameboard[row][col] = ' '
                self.flagcount -= 1
                if self.true_grid[row][col] == 'M':
                    self.goodflags -= 1
        except IndexError:
            return
