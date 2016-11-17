from MM_forestfire_model import * 
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 0,
                 "Color": "red",
                 "r": 0.5}
    return portrayal

grid = CanvasGrid(agent_portrayal, 100, 100, 500, 500)
server = ModularServer(ForestFire,
                       [grid],
                       "Morrissey Forest Fire model",
                       100, 100, .8)
server.port = 8889
server.launch()