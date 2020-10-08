from mineboard import Mineboard
from tkinter import *
from PIL import Image, ImageTk
from math import floor
import time

CELLWIDTH = 26
# colors = [gray,blue,green,red,purple,turquoise,teal,yellow,pink]
COLORS = ['#D4D4D4', '#1876E7', '#4BF139', '#E28415', '#B418E7',
          '#68F5AA', '#17D2D3', '#F7EE2B', '#F22BF7']
DEFAULT_COLOR = '#A0A0A0'


class DisplayWindow(Frame):
    def __init__(self, master=None):
        super(DisplayWindow, self).__init__(master)
        Grid.rowconfigure(master, 0, weight=1)
        Grid.columnconfigure(master, 0, weight=1)
        self.master = master
        self.gridStore = Frame(master)
        # made a mineboard to avoid errors for referencing properties of Mineboard
        self.mineboard = Mineboard(1, 1, 0)
        self.canvas = Canvas(self.master)

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
        # @TODO Do better entry validation
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
        self.canvas.place_forget()
        self.scoreboard.grid_forget()
        self.same_again_bttn.grid_forget()
        self.play_again_bttn.grid_forget()
        if row is None:
            self.master.geometry(f"191x106")
            self.start_screen.grid()
        else:
            self.new_game(row, col, mine)

    def reveal_cell(self, event):
        """Reveals a cell on left mouse click"""
        x = (event.x-2) // CELLWIDTH
        y = (event.y-2) // CELLWIDTH
        if self.mineboard.gamestate is None:
            self.mineboard.reveal_cell(y, x)
            self.update_cells()

    def flag_cell(self, event):
        """Flags a cell on right mouse click"""
        if self.mineboard.gamestate is None:
            x = (event.x-2) // CELLWIDTH
            y = (event.y-2) // CELLWIDTH
            self.mineboard.flag_cell(y, x)
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
                self.canvas.delete(self.cells[i][j])
                self.canvas.create_image(
                    2+j*CELLWIDTH, 2+i*CELLWIDTH, image=MINE, anchor='nw')

    def update_cells(self):
        """updates the display based on currently revealed cells"""
        mineboard = self.mineboard
        gameboard = mineboard.gameboard
        for change in mineboard.changes:
            i, j = change[0], change[1]
            text_val = gameboard[i][j]

            if text_val == 'M':
                self.canvas.delete(self.cells[i][j])
                self.cells[i][j] = self.canvas.create_image(
                    2+j*CELLWIDTH, 2+i*CELLWIDTH, image=EXPLODED, anchor='nw')
                self.reveal_mines(i, j)

            elif text_val == 'F':
                self.canvas.delete(self.cells[i][j])
                self.cells[i][j] = self.canvas.create_image(
                    2+j*CELLWIDTH, 2+i*CELLWIDTH, image=FLAG, anchor='nw')

            elif text_val == ' ':
                self.canvas.delete(self.cells[i][j])
                self.cells[i][j] = self.canvas.create_rectangle(
                    2+j*CELLWIDTH, 2+i*CELLWIDTH, (j+1)*CELLWIDTH, (i+1)*CELLWIDTH, fill=DEFAULT_COLOR, outline="")

            elif text_val in ['0', '1', '2', '3', '4', '5', '6', '7', '8']:
                self.canvas.itemconfig(
                    self.cells[i][j], fill=COLORS[int(text_val)])
                if text_val != '0':
                    # offset here is by 12 pixels
                    self.canvas.create_text(
                        2+j*CELLWIDTH+(CELLWIDTH-1)//2, 2+i*CELLWIDTH+(CELLWIDTH-1)//2, anchor='center', text=f"{text_val}")

        mineboard.changes = []  # removes previous changes
        if mineboard.gamestate is not None:
            # if the game has ended displays game end message and buttons
            self.win_lose_lbl.grid(row=3, column=0, columnspan=4)
            self.win_lose_msg.set(
                f"You {self.mineboard.gamestate}! Play again?")
            self.same_again_bttn.grid(row=4, column=0, columnspan=2)
            self.play_again_bttn.grid(row=4, column=2, columnspan=2)

    def change_display(self, width, height):
        """creates a new grid and displays it upon new game creation"""
        # @TODO Revisit height once we have interaction working
        # @TODO Add scrollbars incase too big a game is made
        self.master.geometry(f"{(width)*CELLWIDTH+2}x{(height+5)*CELLWIDTH}")

        # figure out dimensions of canvas
        self.canvas = Canvas(self.master, width=CELLWIDTH*(width+1)+2,
                             height=CELLWIDTH*(height+1)+2, borderwidth=0, highlightthickness=0)
        self.cells = []

        for y in range(height):
            row = []
            for x in range(width):
                # drawing the cells with a 2 pixel padding and width of 25
                row.append(self.canvas.create_rectangle(
                    2+x*CELLWIDTH, 2+y*CELLWIDTH, (x+1)*CELLWIDTH, (y+1)*CELLWIDTH, fill=DEFAULT_COLOR, outline=""))
            self.cells.append(row)

        self.canvas.place(relx=0, rely=0, anchor='nw')
        self.canvas.bind("<Button-1>", self.reveal_cell)
        self.canvas.bind("<Button-2>", self.flag_cell)
        self.canvas.bind("<Button-3>", self.flag_cell)

        self.canvas.focus_set()


##################################################
def main():
    # creates a window
    root = Tk()
    root.title("Minesweeper")
    app = DisplayWindow(root)
    root.mainloop()
###################################################


if __name__ == "__main__":
    main()
