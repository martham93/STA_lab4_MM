import random
from numpy.random import uniform
import numpy as np
import matplotlib.pyplot as plt
from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import Grid
from mesa.datacollection import DataCollector
from mesa.batchrunner import BatchRunner
from numpy import multiply
from scipy.ndimage.filters import gaussian_filter

class TreeCell(Agent):
    '''
    A tree cell.
    
    Attributes:
        x, y: Grid coordinates
        condition: Can be "Fine", "On Fire", or "Burned Out"
        unique_id: (x,y) tuple. 
    
    unique_id isn't strictly necessary here, but it's good practice to give one to each
    agent anyway.
    '''
    def __init__(self, model, pos, elevation):
        '''
        Create a new tree.
        Args:
            pos: The tree's coordinates on the grid. Used as the unique_id
        '''
        super().__init__(pos, model) #coming from agent class 
        self.pos = pos
        self.unique_id = pos
        self.condition = "Fine"
        self.elevation = elevation 
        
    def step(self):
        '''
        If the tree is on fire, spread it to fine trees nearby.
        '''
        if self.condition == "On Fire":
            neighbors = self.model.grid.get_neighbors(self.pos, moore=False)
            for neighbor in neighbors:
                if neighbor.condition == "Fine" and neighbor.elevation > (self.elevation - 75): #assuming each grid square is 1 mile by 1 mile 
                    neighbor.condition = "On Fire"
            self.condition = "Burned Out"

class ForestFire(Model):
    '''
    Simple Forest Fire model.
    '''
    def __init__(self, height, width, density):
        '''
        Create a new forest fire model.
        
        Args:
            height, width: The size of the grid to model
            density: What fraction of grid cells have a tree in them.
        '''
        
        # Initialize model parameters
        self.height = height
        self.width = width
        self.density = density
        
        # Set up model objects
        self.schedule = RandomActivation(self)
        self.grid = Grid(height, width, torus=False)
        self.dc = DataCollector({"Fine": lambda m: self.count_type(m, "Fine"),
                                "On Fire": lambda m: self.count_type(m, "On Fire"),
                                "Burned Out": lambda m: self.count_type(m, "Burned Out")})
        self.dem = self.fake_surface((self.height, self.width))
        
        # Place a tree in each cell with Prob = density
        for x in range(self.width): #going through and checking every single cell in the 100 by 100 grid
            for y in range(self.height):
                if random.random() < self.density: #if random.random < density then a tree is created else no tree
                    # Create a tree
                    new_tree = TreeCell(self, (x, y), self.dem[x][y])
                    # Set all trees in the first column on fire.
                    if x == 0:
                        new_tree.condition = "On Fire"
                    self.grid[y][x] = new_tree
                    self.schedule.add(new_tree)
        self.running = True           
        
    def step(self):
        '''
        Advance the model by one step.
        '''
        self.schedule.step()
        self.dc.collect(self)
        # Halt if no more fire
        if self.count_type(self, "On Fire") == 0:
            self.running = False
    
    @staticmethod
    def count_type(model, tree_condition):
        '''
        Helper method to count trees in a given condition in a given model.
        '''
        count = 0
        for tree in model.schedule.agents:
            if tree.condition == tree_condition:
                count += 1
        return count
    
    @staticmethod
    def fake_surface(dim=(100, 100), low=500, high=1500, sigma=2): #change to width, height 
        r = uniform(low, high, size=multiply(*dim)).reshape(dim)
        return gaussian_filter(r, sigma=sigma, truncate=9)