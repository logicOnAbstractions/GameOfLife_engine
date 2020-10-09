from utils import *
import numpy as np
import threading
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from logger import get_root_logger

class GameOfLife:
    """ contains the game itself. somewhat like the Simulation obj. in RT """
    def __init__(self, grid_size=100, start_pattern=RANDOM, display=False, movfile=None):
        """

        """
        self.LOG = self.get_logger()
        self.interval       = 50
        self.movfile        = movfile
        self.start_pattern  = start_pattern
        self.grid           = self.init_grid(grid_size)
        self.fig, self.ax   = plt.subplots()
        self.img            = self.ax.imshow(self.grid, interpolation='nearest')

        self.LOG.info(f"Done init in {self.__class__.__name__}.")
        self.run()


    def run(self):
        """ target of the threads that controls the simulation """
        self.LOG.info(f"Running {self.__class__.__name__}")
        ani = animation.FuncAnimation(self.fig, self.update, fargs=(),
                                      frames=10,
                                      interval=self.interval,
                                      save_count=50)
        if self.movfile:
            ani.save(self.movfile, fps=30, extra_args=['-vcodec', 'libx264'])
        plt.show()

    def init_grid(self, grid_size):
        """ initializes a grid according to arguments passed.
            
            return a 2x2 matrix of {ON, OFF} values 
        """

        self.LOG.info(f"Init grid... Pattern: {self.start_pattern}")
        if self.start_pattern == RANDOM:
            return np.random.choice([ON, OFF], grid_size*grid_size, p=[0.2, 0.8]).reshape(grid_size, grid_size)
        else:
            return np.zeros(grid_size * grid_size).reshape(grid_size, grid_size)

    def update(self, dummy):
        """ moves the Game one generation further """
        # copy self.grid since we require 8 neighbors
        # for calculation and we go line by line

        N = self.grid.shape[0]
        self.LOG.info(f"{self.__class__.__name__} updateting.... ")
        tmp_grid = self.grid.copy()
        for i in range(N):
            for j in range(N):
                # compute 8-neghbor sum
                # using toroidal boundary conditions - x and y wrap around
                # so that the simulaton takes place on a toroidal surface.
                total = int((self.grid[i, (j - 1) % N] + self.grid[i, (j + 1) % N] +
                             self.grid[(i - 1) % N, j] + self.grid[(i + 1) % N, j] +
                             self.grid[(i - 1) % N, (j - 1) % N] + self.grid[(i - 1) % N, (j + 1) % N] +
                             self.grid[(i + 1) % N, (j - 1) % N] + self.grid[(i + 1) % N, (j + 1) % N]) / 255)

                # apply Conway's rules
                if self.grid[i, j] == ON:
                    if (total < 2) or (total > 3):
                        tmp_grid[i, j] = OFF
                else:
                    if total == 3:
                        tmp_grid[i, j] = ON
                    # update data
        self.img.set_data(tmp_grid)
        self.grid[:] = tmp_grid[:]
        return self.img,
    
    def add_glider(self, i, j):
        """ adds a glider at the top left (i,j) cell of that area """
        self.LOG.info(f"Adding a glider... ")
        glider = np.array([[0, 0, 255],
                           [255, 0, 255],
                           [0, 255, 255]])
        self.grid[i:i + 3, j:j + 3] = glider
        
    def add_gosper_gun(self, i, j):
        """ adds a thing that spits out gliders """
        self.LOG.info(f"Adding a gosper... ")

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

        self.grid[i:i + 11, j:j + 38] = gun

    def get_logger(self):
        """ inits the logs. should only be if for whatever reason no logger has been defined """
        logger = get_root_logger(BASE_LOGGER_NAME, filename=f'log.log')
        logger.info(f"Initated logger in {self.__class__.__name__} ")
        return logger

# TODO: finish the headless version. we'll ahve to adapt the grid dimensions so it becase a cubic one, or
# define another structure which holds many grid, creating the rd thing.s
class GameOfLifeHeadless(GameOfLife):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self):
        """ for the headless vesrion, we just update the self.grid object by adding data layers in the 3rd axis """
