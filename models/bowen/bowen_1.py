"""
Simulate inherited nuclear family emotional process as defined by Murray Bowen, M.D. from the NIMH family research project.
"""

import logging

import mesa
import mesa.time
import mesa.space
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.UserParam import UserSettableParameter


log = logging.getLogger(__name__)


class PersonAgent(mesa.Agent):

    pass


class BowenModel(mesa.Model):

    pass


def agent_portrayal(agent):

    state_colors = {
        PersonAgent.STATE_FRUSTRATED: "black",
        PersonAgent.STATE_GRATIFIED: "green",
        PersonAgent.STATE_NEED: "red",
    }

    def _color(agent):
        if agent.collision:
            return "blue"
        else:
            return state_colors.get(agent.state)

    portrayal = {
        "Shape": "circle",
        "Color": _color(agent),
        "Filled": not agent.collision,
        "Layer": 0,
        "r": 0.5,
    }
    return portrayal


SIZE = 10


grid = CanvasGrid(agent_portrayal, SIZE, SIZE, 500, 500)
server = ModularServer(BowenModel, [grid], "BowenModel", {})


if __name__ == "__main__":
    import os

    server.launch()
    os.system(f'open "https://localhost:{server.port}"')
