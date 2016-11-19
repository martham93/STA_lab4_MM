from MM_forestfire_model import * 
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 0,
                 "Color": "green",
                 "r": 0.5}

    if agent.condition == "On Fire":
        portrayal["Color"] = "red"
        portrayal["Layer"] = 0

    if agent.condition == 'Burned Out':
     	portrayal["Color"] = 'black'
     	portrayal["Layer"] = 1

    else:
        portrayal["Color"] = "blue"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.2
    return portrayal

grid = CanvasGrid(agent_portrayal, 100, 100, 500, 500)
server = ModularServer(ForestFire,
                       [grid],
                       "Morrissey Forest Fire model",
                       100, 100, .6)
server.port = 8889
server.launch()