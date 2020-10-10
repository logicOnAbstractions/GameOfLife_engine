""" code in this file originally from Geekgs4geeks: https://www.geeksforgeeks.org/program-for-conways-game-of-life/

    will probably be modified here. structure may be sent off to different files etc... for a more flexible structure.

    but core logic from them.
"""

# Python code to implement Conway's Game Of Life
import argparse
import numpy as np
import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from game import GameOfLifeDisplay, GameOfLifeHeadless
from utils import *
import time
import threading
from logger import get_root_logger


class MainProgram:
    """ the runner of the simulation """
    def __init__(self):
        self.LOG        = self.get_logger()
        self.parse_cmdline_args()

        if self.display:
            self.game       = GameOfLifeDisplay(grid_size=self.grid_size, start_pattern=self.start_pattern)
        else:
            self.game       = GameOfLifeHeadless(grid_size=self.grid_size, start_pattern=self.start_pattern)

        self.LOG.info(f"Done init in {self.__class__.__name__}.")

    def parse_cmdline_args(self):
        self.LOG.info(f"Parsing args in {self.__class__.__name__}")
        """ parses stuff.

            to use the values from destinations:
            parser.add_argument('--grid-size', dest='N')
            self.args = parser.parse_args()     # assigns everything to mapping
            (... code.... )

            print(self.args.N)                  # accessing value of --grid-size store as variable N

        """

        # parse arguments
        parser = argparse.ArgumentParser(description="Runs Conway's Game of Life simulation.")

        # assign args to vars ("dest=...")
        parser.add_argument('--grid-size', dest='N', required=False, default=100)  # obv.
        parser.add_argument('--mov-file', dest='movfile', required=False, default=None)  # to save outputs
        parser.add_argument('--interval', dest='interval', required=False, default=100)  # between each generations, ms
        parser.add_argument('--glider', action='store_true', required=False, default=False)  # initial lifeform
        parser.add_argument('--gosper', action='store_true', required=False, default=False)  # spawning lifeform
        parser.add_argument('--display', action='store_true', required=False, default=False)  # if disp. w mplt or just print on console

        # awesome. we now get a mapping of args according to what we wrote above
        self.args = parser.parse_args()
        self.LOG.info(f"Parsing done.")

    @property
    def grid_size(self):
        return self.args.N

    @property
    def glider(self):
        return self.args.glider

    @property
    def gosper(self):
        return self.args.gosper

    @property
    def start_pattern(self):
        """ returning a string so that the caller can just a a single argment &
        parse it on the other side """
        if self.glider:
            return GLIDER
        elif self.gosper:
            return GOSPER
        else:
            return RANDOM

    @property
    def display(self):
        """ determines if we use im.show() & FuncAnim or just dump data into a numpy array 3d"""
        return self.args.display

    def get_logger(self):
        """ inits the logs. should only be if for whatever reason no logger has been defined """
        logger = get_root_logger(BASE_LOGGER_NAME, filename=f'log.log')
        logger.info(f"Initated logger in {self.__class__.__name__} ")
        logger.debug(f'logger debug level msg ')
        logger.info(f'logger info level msg ')
        logger.warning(f'logger warn level msg ')
        logger.error(f'logger error level msg ')
        logger.critical(f'logger critical level msg ')
        return logger


# setting up the values for the grid
ON = 255
OFF = 0
vals = [ON, OFF]


""" I think those are the different grid options """

def randomGrid(N):
    """returns a grid of NxN random values"""
    return np.random.choice(vals, N * N, p=[0.2, 0.8]).reshape(N, N)

def addGlider(i, j, grid):
    """adds a glider with top left cell at (i, j)"""
    glider = np.array([[0, 0, 255],
                       [255, 0, 255],
                       [0, 255, 255]])
    grid[i:i + 3, j:j + 3] = glider

def addGosperGliderGun(i, j, grid):
    """adds a Gosper Glider Gun with top left
    cell at (i, j)"""
    gun = np.zeros(11 * 38).reshape(11, 38)

    gun[5][1] = gun[5][2] = 255
    gun[6][1] = gun[6][2] = 255

    gun[3][13] = gun[3][14] = 255
    gun[4][12] = gun[4][16] = 255
    gun[5][11] = gun[5][17] = 255
    gun[6][11] = gun[6][15] = gun[6][17] = gun[6][18] = 255
    gun[7][11] = gun[7][17] = 255
    gun[8][12] = gun[8][16] = 255
    gun[9][13] = gun[9][14] = 255

    gun[1][25] = 255
    gun[2][23] = gun[2][25] = 255
    gun[3][21] = gun[3][22] = 255
    gun[4][21] = gun[4][22] = 255
    gun[5][21] = gun[5][22] = 255
    gun[6][23] = gun[6][25] = 255
    gun[7][25] = 255

    gun[3][35] = gun[3][36] = 255
    gun[4][35] = gun[4][36] = 255

    grid[i:i + 11, j:j + 38] = gun

def update(frameNum, img, grid, N):
# def update(frameNum, ax, grid, N):
    # copy grid since we require 8 neighbors
    # for calculation and we go line by line
    newGrid = grid.copy()
    for i in range(N):
        for j in range(N):
            # compute 8-neghbor sum
            # using toroidal boundary conditions - x and y wrap around
            # so that the simulaton takes place on a toroidal surface.
            total = int((grid[i, (j - 1) % N] + grid[i, (j + 1) % N] +
                         grid[(i - 1) % N, j] + grid[(i + 1) % N, j] +
                         grid[(i - 1) % N, (j - 1) % N] + grid[(i - 1) % N, (j + 1) % N] +
                         grid[(i + 1) % N, (j - 1) % N] + grid[(i + 1) % N, (j + 1) % N]) / 255)

            # apply Conway's rules
            if grid[i, j] == ON:
                if (total < 2) or (total > 3):
                    newGrid[i, j] = OFF
            else:
                if total == 3:
                    newGrid[i, j] = ON
                # update data

    # ############## works ###############3
    img.set_data(newGrid)
    grid[:] = newGrid[:]
    return img,
    # ############## works ###############3

    # ################## tests ##############
    # grid[:] = newGrid[:]
    # return ax.imshow(grid, interpolation='nearest')
    # ################## tests ##############

def update_headless(grid, N):
    """ side-effect: updates the grid obj. """
    # copy grid since we require 8 neighbors
    # for calculation and we go line by line
    newGrid = grid.copy()
    for i in range(N):
        for j in range(N):
            # compute 8-neghbor sum
            # using toroidal boundary conditions - x and y wrap around
            # so that the simulaton takes place on a toroidal surface.
            total = int((grid[i, (j - 1) % N] + grid[i, (j + 1) % N] +
                         grid[(i - 1) % N, j] + grid[(i + 1) % N, j] +
                         grid[(i - 1) % N, (j - 1) % N] + grid[(i - 1) % N, (j + 1) % N] +
                         grid[(i + 1) % N, (j - 1) % N] + grid[(i + 1) % N, (j + 1) % N]) / 255)

            # apply Conway's rules
            if grid[i, j] == ON:
                if (total < 2) or (total > 3):
                    newGrid[i, j] = OFF
            else:
                if total == 3:
                    newGrid[i, j] = ON
                # update data
    grid[:] = newGrid[:]



def main():
    # parse arguments
    parser = argparse.ArgumentParser(description="Runs Conway's Game of Life simulation.")

    # assign args to vars ("dest")
    parser.add_argument('--grid-size', dest='N', required=False, default=100)                # obv.
    parser.add_argument('--mov-file', dest='movfile', required=False, default=None)           # to save outputs
    parser.add_argument('--interval', dest='interval', required=False, default=100)          # between each generations, ms
    parser.add_argument('--glider', action='store_true', required=False, default=False)        # initial lifeform
    parser.add_argument('--gosper', action='store_true', required=False, default=False)        # spawning lifeform
    parser.add_argument('--display', action='store_true', required=False, default=False)       # if disp. w mplt or just print on console

    # awesome. we now get a mapping of args according to what we wrote above
    args = parser.parse_args()

    # set grid size
    N = 100
    if args.N and int(args.N) > 8:
        N = int(args.N)

    # set animation update interval         - ms?
    updateInterval = 50
    if args.interval:
        updateInterval = int(args.interval)

    # declare grid
    grid = np.array([])

    # check if "glider" demo flag is specified
    if args.glider:
        grid = np.zeros(N * N).reshape(N, N)
        addGlider(1, 1, grid)
    elif args.gosper:
        grid = np.zeros(N * N).reshape(N, N)
        addGosperGliderGun(10, 10, grid)

    else:  # populate grid with random on/off -
        # more off than on
        grid = randomGrid(N)

    # set up animation
    fig, ax = plt.subplots()

    if args.display:                            # what the initial code does
        img = ax.imshow(grid, interpolation='nearest')
        ani = animation.FuncAnimation(fig, update, fargs=(img, grid, N,),
                                      frames=10,
                                      interval=updateInterval,
                                      save_count=50)
        if args.movfile:
            ani.save(args.movfile, fps=30, extra_args=['-vcodec', 'libx264'])
        plt.show()
    else:                                           # new headless mode for simulations, parallele comps.
        generation = 1e2
        x = 0
        while x < generation:
            update_headless(grid, N)
            x += 1

    state = plt.imshow(grid)
    plt.show()


# call main
if __name__ == '__main__':
    mp = MainProgram()

    # main()
