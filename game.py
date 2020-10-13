from utils import *
import numpy as np
import threading
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from logger import get_root_logger

class GameOfLife:
    """ contains the game itself. somewhat like the Simulation obj. in RT

     TODO: add a reset to return game to a default state
     things to reset:
        - grid
        - some way to allow re-providing arguments (--glider etc.)
        - consider making the auto-start optional

     """
    def __init__(self, configs, mode="default", grid_size=100, start_pattern=RANDOM, movfile=None):
        """
        """
        self.LOG            = self.get_logger()
        self.full_configs   = configs               # same as received from mp
        self.mode           = mode
        # those can be set from config file
        self.grid_size      = 10
        self.interval       = 50
        self.movfile        = movfile
        self.start_pattern  = start_pattern
        self.init_args()

        self.grid           = None
        self.init_grid(grid_size)               # sets all elements in grid - any patterns, size, etc.
        self.fig, self.ax   = plt.subplots()
        self.img            = self.ax.imshow(self.grid, interpolation='nearest')

        self.LOG.info(f"Done init in {self.__class__.__name__}.")

    def init_args(self):
        """ parses whatever args we have & sets up this class accordingly """

        for k, v in self.game_configs.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                self.LOG.warning(f"Config file contains an attribute that is not in this class's attribute and therefore has not been set (k,v): {k}, {v}")

        if self.mode != "default":                  # then those will complement/override the default values
            for k, v in self.full_configs[self.mode]["game"].items():
                if hasattr(self, k):
                    setattr(self, k, v)
                else:
                    self.LOG.warning(f"Config file contains an attribute that is not in this class's attribute and therefore has not been set (k,v): {k}, {v}")

    def start(self):
        """ target of the threads that controls the simulation """
        raise NotImplemented

    def reset(self):
        """ allows us to return to some neutral state."""

    def init_grid(self, grid_size):
        """ initializes a grid according to arguments passed.
            
            return a 2x2 matrix of {ON, OFF} values 
        """

        self.LOG.info(f"Init grid... Pattern: {self.start_pattern}")
        if self.start_pattern == RANDOM:
            self.grid = np.random.choice([ON, OFF], grid_size*grid_size, p=[0.2, 0.8]).reshape(grid_size, grid_size)
        else:
            self.grid = np.zeros(grid_size * grid_size).reshape(grid_size, grid_size)
            if self.start_pattern == GLIDER:
                self.add_glider()
            elif self.start_pattern == GOSPER:
                self.add_gosper_gun()

    def update(self, dummy=None):
        """ moves the Game one generation further """
        raise NotImplemented
    
    def add_glider(self, i=1, j=1):
        """ adds a glider at the top left (i,j) cell of that area """
        self.LOG.info(f"Adding a glider... ")
        glider = np.array([[0, 0, 255],
                           [255, 0, 255],
                           [0, 255, 255]])
        self.grid[i:i + 3, j:j + 3] = glider
        
    def add_gosper_gun(self, i=10, j=10):
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

    @property
    def game_configs(self):
        return self.full_configs["default"]["game"]


class GameOfLifeDisplay(GameOfLife):
    def __init__(self, *args, **kwargs):
        """ """
        super().__init__(*args, **kwargs)

    def start(self):
        """ target of the threads that controls the simulation """
        self.LOG.info(f"Running {self.__class__.__name__}")
        ani = animation.FuncAnimation(self.fig, self.update, fargs=(),
                                      frames=10,
                                      interval=self.interval,
                                      save_count=50)
        if self.movfile:
            ani.save(self.movfile, fps=30, extra_args=['-vcodec', 'libx264'])
        plt.show()


    def update(self, dummy=None):
        """ moves the Game one generation further """
        # copy self.grid since we require 8 neighbors
        # for calculation and we go line by line

        N = self.grid.shape[0]
        self.LOG.debug(f"{self.__class__.__name__} updateting.... ")
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


class GameOfLifeHeadless(GameOfLife):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.datacube           = np.zeros(self.grid.shape)
        self.keep_running       = threading.Event()
        self.keep_running.set()
        self.life_thread        = threading.Thread(target=self.run, args=(), name="life")


    def start(self):
        self.life_thread.start()

    def run(self):
        """ instead of img.set_data(...) here we update the grid obj, which is also 3d (3rd axis == generations)"""
        self.LOG.info(f"Life thread starting... ")
        while self.keep_running.is_set():
            self.update()

    def update(self, dummy=None):
        """ update a different object here """
        self.LOG.debug(f"{self.__class__.__name__} update.... ")
        N = self.grid.shape[0]
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
        self.grid[:] = tmp_grid[:]
        self.LOG.debug(f"Sum of the grid: {np.sum(self.grid)}")