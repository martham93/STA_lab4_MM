
# coding: utf-8

# ## Agent Based Models for Forest Fires in Python using the MESA package 

# In[80]:

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

import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.cm as cm
from math import pi
from windrose import WindroseAxes


# In[88]:

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
            
    def get_current_step(self):
        return self.model.schedule.steps
    
    def current_wind_speed(self):
        return self.model.wind.speed[self.get_current_step()]
    
    def current_wind_direction(self):
        return self.model.wind.direction[self.get_current_step()]
    
    def fire_score(self, neighbor):
        return (self.current_wind_speed() * .6) + ((neighbor.elevation - self.elevation) * .4)
    
    def threshold(self):
        min_w_score = self.model.wind.speed_min
        max_w_score = self.model.wind.speed_max
        min_elevation = 500
        max_elevation = 1500
        return np.average(((min_w_score *.6) + ((min_elevation - max_elevation) *.4), (max_w_score * .6) + ((max_elevation - min_elevation)*.4)))
    
    def get_condition(self, neighbor):
        if self.fire_score(neighbor) >= self.threshold():
            return "On Fire"
        else:
            return "On Fire"     
        
    def step(self):
        '''
        If the tree is on fire, spread it to fine trees nearby.
        '''
        if self.condition == "On Fire":
            neighbors = self.model.grid.get_neighbors(self.pos, moore=False)
            for neighbor in neighbors:
                if neighbor.condition == "Fine":    #and neighbor.elevation > (self.elevation - 75): #assuming each grid square is 1 mile by 1 mile 
                    neighbor.condition = self.get_condition(neighbor)  #"On Fire"
            self.condition = "Burned Out"
    


# In[82]:

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
        self.wind = Wind(500, 15, 45, 0, 180)
       
        
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


# In[86]:

class Wind:
    def __init__(self,N, speed_min, speed_max, dir_min, dir_max):
        self.speed = self.wind(N,speed_min, speed_max, dir_min, dir_max)["speed"] #Wind.wind will also work since static
        self.direction = self.wind(N,speed_min, speed_max, dir_min, dir_max)["direction"]
        self.speed_min = speed_min
        self.speed_max = speed_max
        self.dir_min = dir_min
        self.dir_max = dir_max
    
    @staticmethod
    def wind(N,speed_min, speed_max, direction_min, direction_max):
        ws = np.random.random_integers(speed_min, speed_max, N)
        wd = np.random.random_integers(direction_min, direction_max, N)
        df = pd.DataFrame({"speed": ws, "direction": wd})
        return df





