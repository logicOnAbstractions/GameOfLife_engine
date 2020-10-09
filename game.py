from utils import *
import numpy as np
import threading
import time

class GameOfLife:
    """ contains the game itself. somewhat like the Simulation obj. in RT """
    def __init__(self, grid_size=100, start_pattern=RANDOM):
        """ """
        self.start_pattern  = start_pattern
        self.grid           = self.init_grid(grid_size)

        self.life_thread    = threading.Thread(target=self.run(), name="game_of_life")
        self.keep_going     = threading.Event()
        self.keep_going.set()

    def run(self):
        """ target of the threads that controls the simulation """

        while self.keep_going:
            print(f"the show must go on: {time.time()}")
            time.sleep(2)

    def init_grid(self, grid_size):
        """ initializes a grid according to arguments passed.
            
            return a 2x2 matrix of {ON, OFF} values 
        """
        if self.start_pattern == RANDOM:
            return np.random.choice([ON, OFF], grid_size*grid_size, p=[0.2, 0.8]).reshape(grid_size, grid_size)
        else:
            return np.zeros(grid_size * grid_size).reshape(grid_size, grid_size)

    def update(self, frameNum, img, N):
        """ moves the Game one generation further """
        # copy self.grid since we require 8 neighbors
        # for calculation and we go line by line
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
                        tmp_grid.grid[i, j] = OFF
                else:
                    if total == 3:
                        tmp_grid.grid[i, j] = ON
                    # update data
        img.set_data(tmp_grid.grid)
        self.grid[:] = tmp_grid.grid[:]
        return img,
    
    def add_glider(self, i, j):
        """ adds a glider at the top left (i,j) cell of that area """
        glider = np.array([[0, 0, 255],
                           [255, 0, 255],
                           [0, 255, 255]])
        self.grid[i:i + 3, j:j + 3] = glider
        
    def add_gosper_gun(self, i, j):
        """ adds a thing that spits out gliders """
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
