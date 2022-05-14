import logging

import mesa
import mesa.time
import mesa.space

from .ball import Ball


log = logging.getLogger(__name__)


# Independent variables
SIZE = 20
DEFAULT_NUM_BALLS = 10
DEFAULT_NEED_LIMIT = 10
DEFAULT_GRATIFICATION_LIMIT = 10
FRUSTRATION_VARIATION_MAX = 3.0
FRUSTRATION_VARIATION_STEP = 0.1


import os, os.path

MODEL_PATH = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(MODEL_PATH, "mythematical.html"), "r") as f:
    ABOUT_HTML = f.read()


class MythematicalModel(mesa.Model):

    description = ABOUT_HTML

    def __init__(
        self,
        num_balls,
        width,
        height,
        gratification_limit,
        gratification_limit_variation,
        need_limit,
        need_limit_variation,
        frustration_limit,
        frustration_variation,
        show_step_counter,
    ):
        super().__init__()
        self.num_agents = num_balls
        self.schedule = mesa.time.SimultaneousActivation(self)
        self.grid = mesa.space.MultiGrid(width, height, False)
        self.show_step_counter = show_step_counter

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
            a = Ball(
                i,
                self,
                gratification_limit=gratification_limit + gratification_limit_variate,
                need_limit=need_limit + need_limit_variate,
                frustration_limit=frustration_limit,
                frustration_multiplier=self.random.uniform(0, frustration_variation),
            )
            self.schedule.add(a)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

    def step(self):
        self.schedule.step()
