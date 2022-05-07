import os
import sys
import pprint
import logging

import mesa
import mesa.time
import mesa.space

from debug import Debug

logging.getLogger()


pp = pprint.PrettyPrinter(indent=4)

logging.basicConfig(
    stream=sys.stdout,
    filemode="w",
    format="%(levelname)s %(asctime)s - %(message)s",
    level=logging.DEBUG,
)
log = logging.getLogger(__name__)


class BallAgent(mesa.Agent):

    STATE_NEED = 1
    STATE_GRATIFIED = 2
    STATE_FRUSTRATION = 3

    def __init__(self, unique_id, model, gratification_limit):
        super().__init__(unique_id, model)

        # Dependent variables
        self.state = self.STATE_GRATIFIED
        self.gratification_left = gratification_limit

        # Independent variables
        self.frustration_proclivity = 1.0  # TODO: chance variation

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def step(self):
        self.move()
        collisions = self.model.grid.get_cell_list_contents([self.pos])
        if collisions:
            log.info(
                f"Agent {self.unique_id} collisions @ {self.pos}\t::\t{[x.unique_id for x in collisions]}"
            )


class MythematicalModel(mesa.Model):
    def __init__(self, N, width, height):
        self.num_agents = N
        self.schedule = mesa.time.SimultaneousActivation(self)
        self.grid = mesa.space.MultiGrid(width, height, False)

        GRATIFICATION_LIMIT = 3

        for i in range(self.num_agents):
            a = BallAgent(i, self, gratification_limit=GRATIFICATION_LIMIT)
            self.schedule.add(a)

            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

    def step(self):
        self.schedule.step()


from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer


def main_step():
    model = MythematicalModel(10, 35, 35)
    model.step()


def main_web():
    def agent_portrayal(agent):
        portrayal = {
            "Shape": "circle",
            "Color": "red",
            "Filled": "true",
            "Layer": 0,
            "r": 0.5,
        }
        return portrayal

    grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)
    server = ModularServer(
        MythematicalModel, [grid], "Methematical Model", {"N": 100, "width": 10, "height": 10}
    )
    server.port = 8521  # The default
    server.launch()
    os.system(f'open "https://localhost:{server.port}"')


if __name__ == "__main__":
    main_web()
