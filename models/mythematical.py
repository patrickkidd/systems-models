import logging

import mesa
import mesa.time
import mesa.space
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.UserParam import UserSettableParameter


log = logging.getLogger(__name__)


class BallAgent(mesa.Agent):

    STATE_NEED = "need"
    STATE_GRATIFIED = "gratified"
    STATE_FRUSTRATED = "frustrated"

    def __init__(self, unique_id, model, gratification_limit, need_limit):
        super().__init__(unique_id, model)
        self.encountered_this_step = False
        self.collision = False

        # Independent left variables
        self._gratification_limit = gratification_limit
        self._need_limit = need_limit

        # Dependent variables
        self._set_state(self.STATE_GRATIFIED)

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def _set_state(self, state):
        self.state = state
        log.info(f"Agent {self.unique_id} -> {state}")
        if state == self.STATE_GRATIFIED:
            self._gratification_left = self._gratification_limit
        elif state == self.STATE_NEED:
            self._need_state_left = self._need_limit
        else:
            self._need_state_left = None
            self._gratification_left = None

    def on_encounter(self, other):
        """The main algorithm for an encounter between agents."""

        log.info(
            f"Agent {self.unique_id} & {other.unique_id} collision @ {self.pos}\t::\t{other.unique_id}"
        )

        if self.state == self.STATE_GRATIFIED:
            pass
        elif self.state in (self.STATE_NEED, self.STATE_FRUSTRATED) and other.state in (
            self.STATE_NEED,
            self.STATE_FRUSTRATED,
        ):
            self._set_state(self.STATE_GRATIFIED)
            other._set_state(self.STATE_GRATIFIED)

    def step(self):

        self.collision = False

        if self.encountered_this_step:
            return

        # Update state over time.
        if self.state == self.STATE_GRATIFIED:
            self._gratification_left -= 1
            if self._gratification_left == 0:
                self._set_state(self.STATE_NEED)
        elif self.state == self.STATE_NEED:
            self._need_state_left -= 1
            if self._need_state_left == 0:
                self._set_state(self.STATE_FRUSTRATED)

        # Update based on new position, after time-base updates
        self.move()
        encounter = None
        for possible_encounter in self.model.grid.get_cell_list_contents([self.pos]):
            if (
                possible_encounter is not self
                and not possible_encounter.encountered_this_step
            ):
                self.collision = True
                encounter = possible_encounter
                encounter.collision = True
                self.encountered_this_step = True
                self.on_encounter(encounter)
                break
        if encounter:
            self.on_encounter(encounter)


class MythematicalModel(mesa.Model):
    def __init__(
        self,
        N,
        width,
        height,
        gratification_limit,
        gratification_limit_variation,
        need_limit,
        need_limit_variation,
    ):
        super().__init__()
        self.num_agents = N
        self.schedule = mesa.time.SimultaneousActivation(self)
        self.grid = mesa.space.MultiGrid(width, height, False)

        for i in range(self.num_agents):
            if need_limit_variation:
                need_limit_variate = self.random.randrange(
                    -need_limit_variation, need_limit_variation
                )
            else:
                need_limit_variate = 0
            if gratification_limit_variation:
                gratification_limit_variate = self.random.randrange(
                    -gratification_limit_variation, gratification_limit_variation + 1
                )
            else:
                gratification_limit_variate = 0
            a = BallAgent(
                i,
                self,
                gratification_limit=gratification_limit + gratification_limit_variate,
                need_limit=need_limit + need_limit_variate,
            )
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
from mesa.visualization.modules import ChartModule


# Independent variables

SIZE = 20
NUM_BALLS = 10
NEED_LIMIT = 20
GRATIFICATION_LIMIT = 10


def agent_portrayal(agent):

    state_colors = {
        BallAgent.STATE_FRUSTRATED: "black",
        BallAgent.STATE_GRATIFIED: "green",
        BallAgent.STATE_NEED: "red",
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


import os, os.path

MODEL_PATH = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(MODEL_PATH, "mythematical.html"), "r") as f:
    NOTES = f.read()


grid = CanvasGrid(agent_portrayal, SIZE, SIZE, 500, 500)
server = ModularServer(
    MythematicalModel,
    [grid],
    "Mythematical Social Pool Game",
    {
        "N": UserSettableParameter("slider", "N", NUM_BALLS, 2, 40),
        "width": SIZE,
        "height": SIZE,
        "need_limit": UserSettableParameter("slider", "Need Limit", NEED_LIMIT, 1, 30),
        "need_limit_variation": UserSettableParameter(
            "slider", "Need Limit Variation", 0, 0, 10
        ),
        "gratification_limit": UserSettableParameter(
            "slider", "Gratification Limit", GRATIFICATION_LIMIT, 1, 30
        ),
        "gratification_limit_variation": UserSettableParameter(
            "slider", "Gratification Limit Variation", 0, 0, 10
        ),
        "notes": UserSettableParameter("static_text", "Notes", NOTES),
    },
)


if __name__ == "__main__":
    import os

    server.launch()
    os.system(f'open "https://localhost:{server.port}"')
