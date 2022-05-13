import logging

import mesa
import mesa.time
import mesa.space
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.UserParam import UserSettableParameter


log = logging.getLogger(__name__)

# CALHOUN: At all times every ball is in one of three states: in need
# of contact, gratified from a satisfactory contact, or frustrated
# from an unsatisfactory contact.
STATE_NEED = "need"
STATE_GRATIFIED = "gratified"
STATE_FRUSTRATED = "frustrated"

# Independent variables
SIZE = 20
DEFAULT_NUM_BALLS = 10
DEFAULT_NEED_LIMIT = 20
DEFAULT_GRATIFICATION_LIMIT = 10
FRUSTRATION_VARIATION_MAX = 3.0
FRUSTRATION_VARIATION_STEP = 0.1


import os, os.path

MODEL_PATH = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(MODEL_PATH, "mythematical.html"), "r") as f:
    ABOUT_HTML = f.read()


class BallAgent(mesa.Agent):
    def __init__(
        self,
        unique_id,
        model,
        gratification_limit,
        need_limit,
        frustration_limit,
        frustration_multiplier,
    ):
        super().__init__(unique_id, model)

        # Independent variables
        self._gratification_limit = gratification_limit
        self._need_limit = need_limit
        self._frustration_limit = frustration_limit
        self._frustration_multiplier = frustration_multiplier

        # Model state variables
        self.state_counter = 0

        # State step variables
        self.encounter = None

        # Dependent variables
        self._set_state(STATE_GRATIFIED)

    def _set_state(self, state):
        self.state = state
        self.state_counter = 0
        log.info(f"Agent {self.unique_id} -> {state}")

    def step(self):
        # Only allow one encounter per step
        self.encounter = None

        # CALHOUN: Each moves at a constant velocity, as if propelled by some inner force,
        # The physical diameter of each is equal to that of every other ball.
        # All move within a fixed space or area. How often one ball will on the
        # average collide with another will depend upon these three factors,
        # velocity, diameter and area, in relationship to the number of balls
        # present in the area.
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def advance(self):

        # Determine if this agent encounters another on this step.
        other = None
        if not self.encounter:
            for potential_encounter in self.model.grid.get_cell_list_contents(
                [self.pos]
            ):
                if potential_encounter is self:
                    continue
                if not potential_encounter.encounter:
                    encounter = potential_encounter
                    self.encounter = other = potential_encounter
                    potential_encounter.encounter = self
                    break

        state_was = self.state

        if other:

            log.info(
                f"Agent {self.unique_id} & {encounter.unique_id} encounter @ {self.pos} {encounter.pos}\t::\t{encounter.unique_id}"
            )

            if self.state == STATE_GRATIFIED:
                pass

            elif self.state == STATE_NEED:

                if other.state == STATE_GRATIFIED:

                    # CALHOUN: One such ball, "B", by chance encounters a ball which is still in the
                    # gratification state from a prior satisfactory encounter. This latter ball
                    # remains uninfluenced by the encounter with " B" ; it remains stippled.
                    # However, its failure to interact appropriately to the needs of "B" transforms
                    # "B" into a state of frustration indicated by the ball becoming black.
                    self._set_state(STATE_FRUSTRATED)

                elif other.state == STATE_NEED:

                    # CALHOUN: Ball "A" with a bent arrow indicating its path of movement represents
                    # such a ball in the need state of encountering another ball in a like state.
                    # As shown. it does encounter such a ball. Each then gains from the encounter;
                    # each enters a state. which may be designated as gratification. that lasts for
                    # some time after the encounter
                    self._set_state(STATE_GRATIFIED)

                elif other.state == STATE_FRUSTRATED:

                    # CALHOUN: In like fashion, when another ball, "C" , meets a ball in the
                    # frustration state, it too will be thrown into the state of frustration,
                    # in which it will remain for some period of time before returning to the
                    # original need state for contact.
                    self._set_state(STATE_FRUSTRATED)

        if self.state == state_was:
            self.state_counter += 1

        # Time-based updates
        if not other:

            if self.state == STATE_GRATIFIED:

                if self.state_counter >= self._gratification_limit:

                    # CALHOUN: After a specified period of time elapses. each of the stippled
                    # balls will complete its stay in the gratification state and return to the
                    # state of needing further contact with other balls.
                    self._set_state(STATE_NEED)

            elif self.state == STATE_NEED:

                if self.state_counter >= self._need_limit:

                    # CALHOUN:
                    self._set_state(STATE_FRUSTRATED)

            elif self.state == STATE_FRUSTRATED:

                if self.state_counter >= self._frustration_limit:

                    # CALHOUN: it too will be thrown into the state of frustration, in which it
                    # will remain for some period of time before returning to the original need
                    # state for contact.
                    self._set_state(STATE_NEED)

                else:

                    # CALHOUN: The more these balls are frustrated, the more they will try to escape
                    # from the field, the area within which meaningful contacts might occur. They
                    # seek the side pockets of their area of habitation. Here they are not visible
                    # to view; their " dropping out" leads to a lowered estimate of their velocity
                    # in terms of the total path traversed in the contact opportunity area over
                    # extended periods of time.
                    frustration_level = (
                        self.state_counter * self._frustration_multiplier
                    )

                    log.info(
                        f"TODO Implement increasingly 'deviant' behavior for frustrated agents (frustration_level: {frustration_level})."
                    )


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
            a = BallAgent(
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


from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule


def agent_portrayal(agent):

    fill_colors = {
        STATE_FRUSTRATED: "#000000",
        STATE_GRATIFIED: "#00aa00",
        STATE_NEED: "#ff0000",
    }

    fill_colors_encounter = {
        STATE_FRUSTRATED: "#000000aa",
        STATE_GRATIFIED: "#f00aa00aa",
        STATE_NEED: "#ff0000aa",
    }

    stroke_colors = {
        STATE_FRUSTRATED: "#000000",
        STATE_GRATIFIED: "#00ff00",
        STATE_NEED: "#ff0000",
    }

    def _fill_color(agent):
        if agent.encounter:
            return fill_colors_encounter.get(agent.state)
        else:
            return fill_colors.get(agent.state)

    def _stroke_color(agent):
        return stroke_colors.get(agent.state)

    def _x_offset(agent):
        if agent.encounter:
            if id(agent) < id(agent.encounter):
                return -0.15
            else:
                return 0.15
        else:
            return 0

    def _filled(agent):
        return bool(agent.encounter is None)

    def _text(agent):
        if not agent.encounter:
            return str(agent.state_counter)
        else:
            return ""

    def _text_color(agent):
        return "white"

    portrayal = {
        "Shape": "circle",
        "Color": _fill_color(agent),
        "stroke_color": _stroke_color(agent),
        "Filled": _filled(agent),
        "Layer": 0,
        "r": 0.5,
        "x_offset": _x_offset(agent),
        "Need Limit": agent._need_limit,
        "Frustration Limit": agent._frustration_limit,
        "Frustratability": agent._frustration_multiplier,
        "State Counter": agent.state_counter,
        "State": agent.state,
        # "ignoredFeatures": ["Layer"]
        # debug
        # "pos": agent.pos,
        # "unique_id": agent.unique_id,
    }
    if agent.model.show_step_counter:
        portrayal.update(
            {
                "text": _text(agent),
                "text_color": _text_color(agent),
            }
        )

    log.debug(
        f"Agent {agent.unique_id}: ({agent.pos[0]}, {agent.pos[1]}), x_offset: {portrayal.get('x_offset')}"
    )
    return portrayal


grid = CanvasGrid(agent_portrayal, SIZE, SIZE, 600, 600)
server = ModularServer(
    MythematicalModel,
    [grid],
    "Mythematical Social Pool Game",
    {
        "num_balls": UserSettableParameter(
            "slider",
            "Number of balls",
            DEFAULT_NUM_BALLS,
            2,
            40,
            description="Number of balls.",
        ),
        "gratification_limit": UserSettableParameter(
            "slider",
            "Gratification Limit (Steps)",
            DEFAULT_GRATIFICATION_LIMIT,
            1,
            30,
            description="Calhoun: After a specified period of time elapses. each of the stippled balls will complete its stay in the gratification state and return to the state of needing further contact with other balls.",
        ),
        "gratification_limit_variation": UserSettableParameter(
            "slider",
            "Gratification Limit Variation",
            2,
            0,
            10,
            description="Number of steps the gratification limit can vary more or less.",
        ),
        "need_limit": UserSettableParameter(
            "slider",
            "Need Limit (Steps)",
            DEFAULT_NEED_LIMIT,
            1,
            30,
            description="Calhoun: Furthermore, each ball from time to time develops a need state for contacting some other ball in an equivalent need state.",
        ),
        "need_limit_variation": UserSettableParameter(
            "slider",
            "Need Limit Variation",
            3,
            0,
            10,
            description="Number of steps the need limit can vary more or less.",
        ),
        "frustration_limit": UserSettableParameter(
            "slider",
            "Frustration Limit",
            0,
            0,
            10,
            description="Steps in before changing from frustrated to to need state.",
        ),
        "frustration_variation": UserSettableParameter(
            "slider",
            "Frustration Variation",
            0,
            0,
            FRUSTRATION_VARIATION_MAX,
            step=FRUSTRATION_VARIATION_STEP,
            description="Range of randomly selected multiplier for how much more frustrated a ball becomes.",
        ),
        "show_step_counter": UserSettableParameter(
            "checkbox", "Show Steps in Current State", value=False
        ),
        "width": SIZE,
        "height": SIZE,
    },
)


if __name__ == "__main__":
    import os

    server.launch()
    os.system(f'open "https://localhost:{server.port}"')
