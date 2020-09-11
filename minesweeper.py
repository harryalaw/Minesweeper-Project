from random import randint, sample
from tkinter import *
from PIL import Image, ImageTk
from math import floor
import time


# colors = [gray,blue,green,red,purple,turquoise,teal,yellow,pink]
COLORS = ['#D4D4D4', '#1876E7', '#4BF139', '#E28415', '#B418E7',
          '#68F5AA', '#17D2D3', '#F7EE2B', '#F22BF7']
DEFAULT_COLOR = '#A0A0A0'


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


class DisplayWindow(Frame):
    def __init__(self, master=None):
        super(DisplayWindow, self).__init__(master)
        Grid.rowconfigure(master, 0, weight=1)
        Grid.columnconfigure(master, 0, weight=1)
        self.master = master
        self.gridStore = Frame(master)
        # made a mineboard to avoid errors for referencing properties of Mineboard
        self.mineboard = Mineboard(1, 1, 0)
        self.create_widgets()
        self.play_again()

        # define the pictures used by global variables
        global FLAG, MINE, EXPLODED
        FLAG = Image.open('flag.png')
        FLAG = ImageTk.PhotoImage(FLAG)
        MINE = Image.open('mine.png')
        MINE = ImageTk.PhotoImage(MINE)
        EXPLODED = Image.open('mine_exploded.png')
        EXPLODED = ImageTk.PhotoImage(EXPLODED)

    def create_widgets(self):
        self.start_screen()
        self.init_scoreboard()

    def start_screen(self):
        """creates the initial screen that is displayed"""
        self.start_screen = Frame(self.master)
        rows_amount = StringVar()
        cols_amount = StringVar()
        mine_amount = StringVar()
        default = '9'
        default_mines = '10'

        rows_amount.set(default)
        cols_amount.set(default)
        mine_amount.set(default_mines)

        easy_button = Button(self.start_screen, text="Beginner")
        med_button = Button(self.start_screen, text="Intermediate")
        hard_button = Button(self.start_screen, text="Experienced")
        row_lbl = Label(self.start_screen, text="Rows:")
        col_lbl = Label(self.start_screen, text="Columns:")
        mine_lbl = Label(self.start_screen, text="Mines:")
        row_entry = Entry(self.start_screen, text=rows_amount, width=3)
        col_entry = Entry(self.start_screen, text=cols_amount, width=3)
        mine_entry = Entry(self.start_screen, text=mine_amount, width=3)
        start_button = Button(self.start_screen, text="Start Game")

        easy_button.grid(row=0, column=0, sticky='ew')
        med_button.grid(row=1, column=0, sticky='ew')
        hard_button.grid(row=2, column=0, sticky='ew')
        row_lbl.grid(row=0, column=1)
        col_lbl.grid(row=1, column=1)
        mine_lbl.grid(row=2, column=1)
        row_entry.grid(row=0, column=3)
        col_entry.grid(row=1, column=3)
        mine_entry.grid(row=2, column=3)
        start_button.grid(row=3, column=0, columnspan=3, sticky='ews')

        def set_entries(row, col, mines):
            """changes the values of the three entry boxes"""
            rows_amount.set(row)
            cols_amount.set(col)
            mine_amount.set(mines)

        easy_button["command"] = lambda: set_entries('9', '9', '10')
        med_button["command"] = lambda:  set_entries('16', '16', '40')
        hard_button["command"] = lambda: set_entries('20', '24', '99')
        start_button["command"] = lambda: self.new_game(
            cols_amount.get(), rows_amount.get(), mine_amount.get())

    def init_scoreboard(self):
        self.scoreboard = Frame(self.master)

        self.now = StringVar()
        self.start_time = time.time()
        self.time = Label(self.scoreboard)
        self.time["textvariable"] = self.now
        self.time.grid(row=0, column=0, columnspan=4, sticky='n')

        self.mine_lbl = Label(self.scoreboard)
        self.mines_left = StringVar()
        self.mine_lbl["textvariable"] = self.mines_left
        self.mine_lbl.grid(row=1, column=0, columnspan=4, sticky='n')
        self.mines_left.set("10 mines left")

        self.win_lose_lbl = Label(self.scoreboard)
        self.win_lose_msg = StringVar()
        self.win_lose_lbl['textvariable'] = self.win_lose_msg

        self.same_again_bttn = Button(self.scoreboard, text='Same Again?')
        self.same_again_bttn["command"] = lambda: self.play_again(
            self.mineboard.width, self.mineboard.height, self.mineboard.minecount)
        self.play_again_bttn = Button(
            self.scoreboard, text='Change size', command=self.play_again)

    def timer_update(self):
        """updates the time displayed on self.time"""
        if self.mineboard.gamestate is not None:
            return
        time_so_far = round(time.time()-self.start_time)
        if time_so_far == 1:
            self.now.set(f"Time so far: {time_so_far} second")
        else:
            self.now.set(f"Time so far: {time_so_far} seconds")
        self.after(1000, self.timer_update)  # calls this function every second

    def new_game(self, width, height, minecount):
        """Initialises a new game board"""
        self.start_screen.grid_forget()
        try:  # deals with incorrectly filled in entries on start screen
            width, height, minecount = int(width), int(height), int(minecount)
        except ValueError:  # defaults to an easy board
            width, height, minecount = 9, 9, 10
        self.mineboard = Mineboard(
            width, height, minecount)
        self.change_display(width, height)
        self.scoreboard.grid(row=1, column=0, sticky='n')
        self.win_lose_lbl.grid_remove()
        self.start_time = time.time()  # initial time for the game
        self.timer_update()  # initial time display

    def play_again(self, row=None, col=None, mine=None):
        """Either returns to the initial screen to change the settings
           or starts a new game with same dimensions"""
        self.gridStore.grid_forget()
        self.scoreboard.grid_forget()
        self.same_again_bttn.grid_forget()
        self.play_again_bttn.grid_forget()
        if row is None:
            self.master.geometry(f"191x106")
            self.start_screen.grid()
        else:
            self.new_game(row, col, mine)

    def reveal_cell(self, row, col):
        """Reveals a cell on left mouse click"""
        if self.mineboard.gamestate is None:
            self.mineboard.reveal_cell(row, col)
            self.update_cells()

    def flag_cell(self, row, col):
        """Flags a cell on right mouse click"""
        if self.mineboard.gamestate is None:
            self.mineboard.flag_cell(row, col)
            self.update_cells()
            mines_rem = self.mineboard.minecount - self.mineboard.flagcount
            # updates the mines_left label
            if mines_rem == 1:
                self.mines_left.set(f"{mines_rem} mine left")
            else:
                self.mines_left.set(f"{mines_rem} mines left")

    def reveal_mines(self, row, col):
        """reveals location of all mines when any mine is pressed"""
        for loc in self.mineboard.mine_places:
            if loc != [row, col]:
                i, j = loc[0], loc[1]
                if self.mineboard.gameboard[i][j] == 'F':
                    continue
                self.labels[i][j].config(text='', width=2)
                self.labels[i][j].config(
                    image=MINE, borderwidth=0, padx=0, pady=0)
                self.labels[i][j].pack(fill=BOTH)

    def update_cells(self):
        """updates the display based on currently revealed cells"""
        mineboard = self.mineboard
        gameboard = mineboard.gameboard
        for change in mineboard.changes:
            i, j = change[0], change[1]
            text_val = gameboard[i][j]
            currLbl = self.labels[i][j]
            if text_val == 'M':
                currLbl.config(text='', width=2)
                currLbl.config(image=EXPLODED, borderwidth=0, padx=0, pady=0)
                # clears text and removes padding for image
                # on separate lines since otherwise the images do not center properly
                self.reveal_mines(i, j)
            elif text_val == 'F':
                currLbl.config(text='', width=2)
                currLbl.config(image=FLAG, borderwidth=0, padx=0,
                               pady=0)
                # clears text and removes padding for image
                # on separate lines else the images do not center properly
            elif text_val == ' ':
                currLbl.config(image='', borderwidth=1, padx=1,
                               pady=1, text=' ', bg=DEFAULT_COLOR, width=2)
                # resets the cell to original settings
            elif text_val in ['0', '1', '2', '3', '4', '5', '6', '7', '8']:
                currLbl.config(text=text_val, bg=COLORS[int(text_val)])
                if text_val == '0':
                    currLbl.config(text=' ')
        mineboard.changes = []  # removes previous changes
        if mineboard.gamestate is not None:
            # if the game has ended displays game end message and buttons
            self.win_lose_lbl.grid(row=3, column=0, columnspan=4)
            self.win_lose_msg.set(
                f"You {self.mineboard.gamestate}! Play again?")
            self.same_again_bttn.grid(row=4, column=0, columnspan=2)
            self.play_again_bttn.grid(row=4, column=2, columnspan=2)

    """
  change_display was helped by:
  https://stackoverflow.com/questions/10865116/tkinter-creating-buttons-in-for-loop-passing-command-arguments
  """

    def change_display(self, width, height):
        """creates a new grid and displays it upon new game creation"""
        self.master.geometry(f"{width*25}x{(height+4)*25}")
        self.gridStore.destroy()
        self.gridStore = Frame(self.master)
        self.gridStore.grid(row=0, column=0, sticky='n')

        self.cells = [[' ' for _ in range(width)] for _ in range(height)]
        self.labels = [[' ' for _ in range(width)] for _ in range(height)]
        for i in range(height):
            for j in range(width):
                self.cells[i][j] = Frame(
                    self.gridStore, borderwidth=1, width=24, height=24)
                currCell = self.cells[i][j]
                currCell.grid(row=i, column=j, sticky='news')
                currCell.pack_propagate(0)
                self.labels[i][j] = Label(
                    currCell, bg=DEFAULT_COLOR, text=' ', width=2)
                currLbl = self.labels[i][j]
                currLbl.pack(fill=BOTH)
                currLbl.bind("<Button-1>", lambda event, i=i,
                             j=j: self.reveal_cell(i, j))
                currLbl.bind("<Button-2>", lambda event,
                             i=i, j=j: self.flag_cell(i, j))
                currLbl.bind("<Button-3>", lambda event,
                             i=i, j=j: self.flag_cell(i, j))
        for i in range(height):
            Grid.rowconfigure(self.gridStore, i, weight=1)
        for j in range(width):
            Grid.columnconfigure(self.gridStore, j, weight=1)


##################################################
# creates a window
root = Tk()
root.title("Minesweeper")
app = DisplayWindow(root)
root.mainloop()
###################################################
