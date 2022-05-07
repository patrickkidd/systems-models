import os
import sys
import logging

import mesa
import mesa.time
import mesa.space

logging.getLogger()


logging.basicConfig(
    stream=sys.stdout,
    filemode="w",
    format="%(levelname)s %(asctime)s - %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)


class BallAgent(mesa.Agent):

    STATE_NEED = 1
    STATE_GRATIFIED = 2
    # STATE_FRUSTRATION = 3

    def __init__(self, unique_id, model, gratification_limit):
        super().__init__(unique_id, model)
        self.encountered_this_step = False
        self.collision = False
        self._gratification_limit = gratification_limit

        # Dependent variables
        self._set_state(self.STATE_GRATIFIED)

        # Independent variables
        self.frustration_proclivity = 1.0  # TODO: chance variation

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def _set_state(self, state):
        self.state = state
        if state == self.STATE_GRATIFIED:
            self.gratification_left = self._gratification_limit
        else:
            self.gratification_left = 0

    def on_encounter(self, other):
        """The main algorithm for an encounter between agents."""

        log.info(
            f"Agent {self.unique_id} & {other.unique_id} collision @ {self.pos}\t::\t{other.unique_id}"
        )

        if self.state == self.STATE_GRATIFIED:
            pass
        elif self.state == self.STATE_NEED:
            if other == self.STATE_NEED:
                self.state = self.STATE_GRATIFIED
                other.state = self.STATE_GRATIFIED

    def step(self):

        self.collision = False

        if self.encountered_this_step:
            return

        # Update state over time.
        if self.state == self.STATE_GRATIFIED:
            self.gratification_left -= 1
            if self.gratification_left == 0:
                self.state = self.STATE_NEED
                log.info(f"Agent {self.unique_id} -> STATE_NEED")

        self.move()
        for encounter in self.model.grid.get_cell_list_contents([self.pos]):
            if encounter is not self and not encounter.encountered_this_step:
                self.collision = True
                encounter.collision = True
                self.encountered_this_step = True
                self.on_encounter(encounter)
                break


class MythematicalModel(mesa.Model):
    def __init__(self, N, width, height):
        super().__init__()
        self.num_agents = N
        self.schedule = mesa.time.SimultaneousActivation(self)
        self.grid = mesa.space.MultiGrid(width, height, False)

        for i in range(self.num_agents):
            gratification_limit = self.random.randrange(3, 10)
            a = BallAgent(i, self, gratification_limit=gratification_limit)
            self.schedule.add(a)

            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

    def step(self):
        for agent in self.schedule.agents:
            agent.encountered_this_step = False
        self.schedule.step()


from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer


def main_step():
    model = MythematicalModel(2, 35, 35)
    model.step()


def main_web():
    def agent_portrayal(agent):

        state_colors = {
            # BallAgent.STATE_FRUSTRATION: "black",
            BallAgent.STATE_GRATIFIED: "green",
            BallAgent.STATE_NEED: "red",
        }

        def _color(agent):
            if agent.collision:
                log.info("collision")
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

    class Server(ModularServer):
        verbose = False

    grid = CanvasGrid(agent_portrayal, 20, 20, 500, 500)
    server = ModularServer(
        MythematicalModel,
        [grid],
        "Methematical Model",
        {"N": 10, "width": 20, "height": 20},
    )
    server.port = 8521  # The default
    server.launch()
    os.system(f'open "https://localhost:{server.port}"')


if __name__ == "__main__":
    main_web()
